from collections import OrderedDict
from copy import copy

from hcube.api.exceptions import ConfigurationError
from hcube.api.models.aggregation import Sum
from hcube.api.models.cube import Cube
from hcube.api.models.dimensions import Dimension


class AggregatingMaterializedViewMeta(type):
    """
    This is a special type of materialized view that is obtained by removing some of the dimensions
    from a cube and aggregating the metrics for rows that are left the same after the dimensions
    are removed.

    This leads to reduction of the size of the cube.

    To simplify matters, at present the only aggregation supported is SUM() and we do not support
    renaming the metric in the aggregation. This should simplify implementation of automatic
    materialized view detection/use.
    """

    default_metric_aggregation = Sum

    def __new__(cls, *args, **kwargs):
        new_cls = super().__new__(cls, *args, **kwargs)
        new_cls._process_attrs()
        new_cls.cube_ = new_cls._create_cube()
        return new_cls

    def _process_attrs(cls):
        # we do not process the top-level class in the hierarchy
        if cls.__name__ == "AggregatingMaterializedView":
            return
        if not hasattr(cls, "src_cube"):
            raise ConfigurationError("Materialized view instance must have a `src_cube` class attr")
        if not issubclass(cls.src_cube, Cube):
            raise ConfigurationError("Attribute `src_cube` must be a `Cube` subclass")
        # registers this materialized view with `cube`
        cls.src_cube._materialized_views.append(cls)
        # process dimension specification
        excludes_dims = getattr(cls, "excluded_dimensions", None)
        preserved_dims = getattr(cls, "preserved_dimensions", None)
        if excludes_dims and preserved_dims:
            raise ConfigurationError(
                "`excluded_dimensions` and `preserved_dimensions` attrs are mutually exclusive"
            )
        cls._dimensions = OrderedDict()
        if excludes_dims:
            for dim_name in excludes_dims:
                if dim_name not in cls.src_cube._dimensions:
                    raise ConfigurationError(
                        f"Excluded dimension `{dim_name} is not part of cube definition"
                    )
            # we want to have the same order in the dims as in the cube
            my_meta = cls.Clickhouse if hasattr(cls, "Clickhouse") else None
            cube_meta = cls.src_cube.Clickhouse if hasattr(cls.src_cube, "Clickhouse") else None
            # decide on the sorting key - use own setting if available, otherwise use cube setting
            sorting_key = []
            if my_meta:
                sorting_key = getattr(my_meta, "sorting_key", [])
            if not sorting_key and cube_meta:
                sorting_key = getattr(cube_meta, "sorting_key", [])
            # add dimensions from sorting key
            for dim_name in sorting_key:
                if dim_name not in excludes_dims:
                    cls._dimensions[dim_name] = cls._copy_dim(cls.src_cube._dimensions[dim_name])
            # add any remaining dimensions
            for dim_name, dim in cls.src_cube._dimensions.items():
                if dim_name not in excludes_dims and dim_name not in cls._dimensions:
                    cls._dimensions[dim_name] = cls._copy_dim(dim)
        elif preserved_dims:
            for dim_name in preserved_dims:
                dim = cls.src_cube.dimension_by_name(dim_name)
                if not dim:
                    raise ConfigurationError(
                        f"Preserved dimension `{dim_name} is not part of cube definition"
                    )
                cls._dimensions[dim_name] = cls._copy_dim(dim)
        else:
            raise ConfigurationError(
                "`excluded_dimensions` or `preserved_dimensions` attr is required"
            )
        # process metric aggregation specification
        cls._aggregations = []
        if cls.aggregated_metrics:
            for m_name in cls.aggregated_metrics:
                metric = cls.src_cube.metric_by_name(m_name)
                if not metric:
                    raise ConfigurationError(
                        f"Aggregated metric `{m_name} is not part of cube definition"
                    )
                cls._aggregations.append(Sum(metric))
        else:
            raise ConfigurationError("`aggregated_metrics` attr is required")

    def _create_cube(cls):
        """
        Creates a new cube class based on the materialized view.
        """
        if cls.__name__ == "AggregatingMaterializedView":
            return
        cube_name = f"{cls.__name__}Cube"
        cube_attrs = {
            **cls._dimensions,
            **{agg.dim_or_metric.name: agg.dim_or_metric for agg in cls._aggregations},
        }
        if hasattr(cls, "Clickhouse"):
            cube_attrs["Clickhouse"] = copy(cls.Clickhouse)
            cube_attrs["Clickhouse"].table_name = cls.__name__
        else:
            cube_attrs["Clickhouse"] = type("Clickhouse", (), {"table_name": cls.__name__})
        return type(cube_name, (Cube,), cube_attrs)

    @staticmethod
    def _copy_dim(dim: Dimension):
        """
        Create a new instance of the dimension to prevent a dimension being referenced from the
        parent cube and the mv at the same time.
        """
        new = dim.__class__()
        new.__dict__.update(dim.__dict__)
        return new


class AggregatingMaterializedView(metaclass=AggregatingMaterializedViewMeta):
    excluded_dimensions: list = []
    preserved_dimensions: list = []
    aggregated_metrics: list = []
    projection: bool = False  # should this be a projection rather than a materialized view
    preserve_sign: bool = True  # should we preserve the sign column in the materialized view

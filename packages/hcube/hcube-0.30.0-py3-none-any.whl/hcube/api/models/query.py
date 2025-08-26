import typing
from typing import Any, List, Optional, Type, Union

from hcube.api.exceptions import ConfigurationError, ConsistencyError
from hcube.api.models.aggregation import Aggregation, AggregationOp, ArrayAgg, Count
from hcube.api.models.dimensions import Dimension
from hcube.api.models.filters import (
    ComparisonFilter,
    ComparisonType,
    EqualityFilter,
    Filter,
    FilterCombinator,
    IsNullFilter,
    ListFilter,
    NegativeListFilter,
    OverlapFilter,
    SubstringFilter,
    SubstringMultiValueFilter,
    Wrapper,
)
from hcube.api.models.group_filters import ComparisonGroupFilter, GroupFilter
from hcube.api.models.injections import Injection
from hcube.api.models.metrics import Metric
from hcube.api.models.ordering import OrderDirection, OrderSpec
from hcube.api.models.transforms import JoinTransform, Transform, VerbatimTransform

if typing.TYPE_CHECKING:
    # otherwise we get a circular import
    from hcube.api.models.materialized_views import AggregatingMaterializedView


class CubeQuery:
    """
    Describes a cube query - i.e. filters, groups, aggregations and ordering
    """

    FILTER_SHORTHANDS = {
        "in": ListFilter,
        "isnull": IsNullFilter,
        "not_in": NegativeListFilter,
        "overlap": OverlapFilter,
    }

    def __init__(self, cube: Type["Cube"]):  # noqa - cannot import Cube - circular import
        self.cube = cube
        self.filters: List[Filter] = []
        self.aggregations: List[Aggregation] = []
        self.groups: List[Dimension] = []
        self.group_filters: List[GroupFilter] = []
        self.orderings: List[OrderSpec] = []
        self.transforms: List[Transform] = []
        self.limit: Optional[int] = None
        self.offset: Optional[int] = None
        self.injections: List[Injection] = []

    def __str__(self):
        groups = ", ".join(str(group) for group in self.groups)
        aggs = ", ".join(str(agg) for agg in self.aggregations)
        filters = ", ".join(str(fltr) for fltr in self.filters)
        return f"CubeQuery(groups=[{groups}],\n  aggregations=[{aggs}],\n  filters=[{filters}])"

    def filter(
        self, *fltrs: Filter, extra_: Optional[dict] = None, **named_filters: Any
    ) -> "CubeQuery":
        """
        `extra_` is named with the underscore to avoid conflict with a possible `extra` keyword
        argument used as a filter name.
        """
        for fltr in fltrs:
            if isinstance(fltr, FilterCombinator):
                self._check_combinator(fltr)
            elif isinstance(fltr, Wrapper):
                fltr = self._resolve_wrapper(fltr)
            else:
                fltr.dimension = self._resolve_dim(fltr.dimension)
            self.filters.append(fltr)
        for spec, value in named_filters.items():
            self.filters.append(self.resolve_shorthand(spec, value, extra=extra_))
        return self

    def aggregate(self, *aggregations: Aggregation, **named_aggregs) -> "CubeQuery":
        self.aggregations.extend(aggregations)
        for name, aggreg in named_aggregs.items():
            aggreg.name = name
            self.aggregations.append(aggreg)
        for aggreg in self.aggregations:
            self._postprocess_aggregation(aggreg)
        return self

    def group_by(self, *dims: Union[str, Dimension]) -> "CubeQuery":
        for dim in dims:
            self.groups.append(self._resolve_dim(dim))
        return self

    def group_filter(self, *filters: GroupFilter, **named_filters: Any) -> "CubeQuery":
        for fltr in filters:
            self._postprocess_aggregation(fltr.agg)
            self.group_filters.append(fltr)
        for spec, value in named_filters.items():
            self.group_filters.append(self._resolve_group_filter_shorthand(spec, value))
        return self

    def order_by(self, *orders: Union[str, OrderSpec]) -> "CubeQuery":
        for order in orders:
            if not isinstance(order, OrderSpec):
                direction = OrderDirection.DESC if order.startswith("-") else OrderDirection.ASC
                oname = order.lstrip("-")
                dim = self._resolve_dim_metric_or_aggregation(oname)
                order = OrderSpec(dimension=dim, direction=direction)
            else:
                order.dimension = self._resolve_dim_metric_or_aggregation(order.dimension)
            self.orderings.append(order)
        return self

    def possible_materialized_views(self) -> [Type["AggregatingMaterializedView"]]:
        """
        Returns a list of materialized views that can be used for this query.
        """
        mat_views = [mv for mv in self.cube._materialized_views if not mv.projection]
        if not mat_views:
            return []
        # we only support Sum aggregation in materialized views at present, so any other
        # aggregation makes use of materialized views impossible
        if not all(agg.op == AggregationOp.SUM for agg in self.aggregations):
            return []
        # let's check materialized views against the used dims and metrics
        used_dim_names = set()
        if self.groups:
            used_dim_names |= {group.name for group in self.groups}
            for fltr in self.filters:
                if isinstance(fltr, FilterCombinator):
                    used_dim_names |= {dim.name for dim in fltr.get_involved_dimensions()}
                else:
                    used_dim_names.add(fltr.dimension.name)
            # when analyzing orderings, we are only interested in cube's own dimensions and metrics
            # - transforms and aggregations are dealt with separately
            used_dim_names |= {
                order.dimension.name
                for order in self.orderings
                if order.dimension.name in self.cube._dimensions
                or order.dimension.name in self.cube._metrics
            }
            used_dim_names |= {
                agg.distinct.name
                for agg in self.aggregations
                if isinstance(agg, Count) and agg.distinct
            }
            for transform in self.transforms:
                if not transform.dimension:
                    # this can happen for the VerbatimTransform.
                    if isinstance(transform, VerbatimTransform):
                        if transform.involved_dimensions is None:
                            # we assume this transform isn't safe to use with any materialized view
                            return []
                        used_dim_names |= {dim.name for dim in transform.involved_dimensions}
                    else:
                        raise ConfigurationError(
                            "Transform without dimension is not supported in this context"
                        )
                else:
                    used_dim_names.add(transform.dimension.name)
            # check aggregation filters
            for agg in self.aggregations:
                for fltr in agg.filters:
                    used_dim_names.add(fltr.dimension.name)
        else:
            # if there is no grouping, we will return all dimensions
            used_dim_names |= {dim.name for dim in self.cube._dimensions.values()}

        used_metrics = {agg.dim_or_metric.name for agg in self.aggregations if agg.dim_or_metric}
        if not self.groups:
            # if there are no groups, we return all metrics
            used_metrics = {metric.name for metric in self.cube._metrics.values()}
        out = []
        for mv in mat_views:
            mv_dim_names = {dim.name for dim in mv._dimensions.values()}
            mv_metric_names = {agg.dim_or_metric.name for agg in mv._aggregations}
            if used_dim_names.issubset(mv_dim_names) and used_metrics.issubset(mv_metric_names):
                out.append(mv)
        return out

    def transform(self, *transforms: Transform, **name_to_transform: Transform):
        for transform in transforms:
            self.transforms.append(transform)
        for name, transform in name_to_transform.items():
            transform.name = name
            self.transforms.append(transform)
        # translate dimension names if used
        for transform in self.transforms:
            transform.dimension = self._resolve_dim(transform.dimension)
            if isinstance(transform, JoinTransform):
                # resolve dimensions named by string in join filters
                for jf in transform.join_filters:
                    if isinstance(jf.dimension, str):
                        try:
                            # try to resolve the dimension in the context of the query
                            jf.dimension = self._resolve_dim(jf.dimension)
                        except ConfigurationError:
                            # dimension must be from the joined cube
                            jf.dimension = transform.joined_dim.cube.dimension_by_name(jf.dimension)
        return self

    def inject_groups(self, injection: Injection):
        self.injections.append(injection)
        return self

    def resolve_shorthand(self, spec: str, value: Any, extra: Optional[dict] = None) -> Filter:
        parts = spec.split("__")
        if len(parts) == 1:
            return EqualityFilter(dimension=self._resolve_dim(parts[0]), value=value, extra=extra)
        if len(parts) != 2:
            raise ValueError("filter spec must be in format `name`__`filter`")
        dim_name, shorthand = parts
        fltr_cls = self.FILTER_SHORTHANDS.get(shorthand)
        if fltr_cls:
            return fltr_cls(self._resolve_dim(dim_name), value, extra=extra)
        if shorthand in ("gt", "gte", "lt", "lte"):
            return ComparisonFilter(
                dimension=self._resolve_dim(dim_name),
                comparison=ComparisonType[shorthand.upper()],
                value=value,
                extra=extra,
            )
        if shorthand in ("contains", "icontains"):
            return SubstringFilter(
                dimension=self._resolve_dim(dim_name),
                value=value,
                case_sensitive=shorthand == "contains",
                extra=extra,
            )
        if shorthand in ("mcontains", "imcontains"):
            return SubstringMultiValueFilter(
                dimension=self._resolve_dim(dim_name),
                values=value,
                case_sensitive=shorthand == "mcontains",
                extra=extra,
            )
        raise ValueError(f"unsupported filter `{shorthand}`")

    def _resolve_group_filter_shorthand(self, spec: str, value: Any) -> GroupFilter:
        parts = spec.split("__")
        if len(parts) != 2:
            raise ValueError("filter spec must be in format `name`__`filter`")
        dim_name, shorthand = parts
        if shorthand in ("gt", "gte", "lt", "lte"):
            return ComparisonGroupFilter(
                agg=self._resolve_aggregation(dim_name),
                comparison=ComparisonType[shorthand.upper()],
                value=value,
            )
        raise ValueError(f"unsupported filter `{shorthand}`")

    def _resolve_dim(
        self, dim: Union[str, Dimension, Transform]
    ) -> Optional[Union[Dimension, Transform]]:
        if dim is None:
            return None

        if isinstance(dim, Dimension):
            if dim.cube != self.cube:
                # dimension from another cube - we need to check if it is joined
                # to this cube and either let it be or raise an error
                for transform in self.transforms:
                    if (
                        isinstance(transform, JoinTransform)
                        and transform.target_dim.cube is dim.cube
                    ):
                        return dim
                raise ConsistencyError(
                    f"Dimension '{dim}' is not associated with cube: {self.cube}"
                )
            return self._check_own_dimension(dim)

        if isinstance(dim, Transform):
            return dim

        for transform in self.transforms:
            if transform.name == dim:
                return transform
            if isinstance(transform, JoinTransform) and transform.target_dim.name == dim:
                return transform.target_dim

        return self.cube.dimension_by_name(dim)

    def _resolve_dim_or_metric(
        self, dim_or_metric: Union[str, Metric, Dimension]
    ) -> Union[Metric, Dimension, Transform]:
        if isinstance(dim_or_metric, Metric):
            return self._check_own_metric(dim_or_metric)
        elif isinstance(dim_or_metric, Dimension):
            return self._resolve_dim(dim_or_metric)
        else:
            for transform in self.transforms:
                if transform.name == dim_or_metric:
                    return transform
            try:
                return self.cube.metric_by_name(dim_or_metric)
            except ConfigurationError:
                try:
                    return self.cube.dimension_by_name(dim_or_metric)
                except ConfigurationError:
                    raise ConfigurationError(
                        f"Unknown dimension or metric: {dim_or_metric}"
                    ) from None

    def _resolve_dim_metric_or_aggregation(self, name: Union[str, Metric, Dimension]) -> Any:
        try:
            return self._resolve_dim_or_metric(name)
        except ConfigurationError:
            if dims := [agg for agg in self.aggregations if agg.name == name]:
                return dims[0]
            else:
                raise ConfigurationError(
                    f"Order by '{name}' is not possible - it is neither dimension, "
                    "metric nor aggregation"
                ) from None

    def _resolve_metric(self, metric: Union[str, Metric]) -> Metric:
        if isinstance(metric, Metric):
            return self._check_own_metric(metric)
        else:
            return self.cube.metric_by_name(metric)

    def _resolve_aggregation_filters(self, aggreg: Aggregation):
        new_filters = []
        for fltr in aggreg.filters:
            if isinstance(fltr, dict):
                for key, value in fltr.items():
                    new_filters.append(self.resolve_shorthand(key, value))
            else:
                new_filters.append(fltr)
        aggreg.filters = new_filters

    def _resolve_aggregation(self, name):
        for aggreg in self.aggregations:
            if aggreg.name == name:
                return aggreg
        raise ConfigurationError(f"Aggregation '{name}' is not defined")

    def _check_own_dimension(self, dim: Dimension) -> Dimension:
        if dim not in self.cube._dimensions.values():
            raise ConsistencyError(f'Dimension "{dim}" is not associated with cube: {self.cube}')
        return dim

    def _check_own_metric(self, metric: Metric) -> Metric:
        if metric not in self.cube._metrics.values():
            raise ConsistencyError(f'Metric "{metric}" is not associated with cube: {self.cube}')
        return metric

    def _check_combinator(self, combinator: FilterCombinator):
        new_filters = []
        for fltr in combinator.filters:
            if isinstance(fltr, FilterCombinator):
                self._check_combinator(fltr)
                new_filters.append(fltr)
            elif isinstance(fltr, Wrapper):
                new_filters.append(self._resolve_wrapper(fltr))
            else:
                fltr.dimension = self._resolve_dim(fltr.dimension)
                new_filters.append(fltr)
        combinator.filters = new_filters

    def _resolve_wrapper(self, wrapper: Wrapper) -> Filter:
        return self.resolve_shorthand(wrapper.key, wrapper.value)

    def _postprocess_aggregation(self, aggreg):
        if aggreg.filters:
            self._resolve_aggregation_filters(aggreg)
        if aggreg.dim_or_metric:
            # resolve the metric when it was given as a string
            aggreg.dim_or_metric = self._resolve_dim_or_metric(aggreg.dim_or_metric)
        elif isinstance(aggreg, (Count, ArrayAgg)) and aggreg.distinct:
            aggreg.distinct = self._resolve_dim(aggreg.distinct)
        else:
            if not aggreg.allow_metric_none:
                raise ConfigurationError(
                    f"Aggregation '{aggreg.__class__}' cannot have empty metric"
                )

    def __getitem__(self, key):
        if isinstance(key, slice):
            self.limit = key.stop
            if key.start:
                self.offset = key.start
                if self.limit:
                    self.limit -= key.start
            return self
        else:
            raise ConfigurationError(f"Unsupported slicing type: {key} ({type(key)})")

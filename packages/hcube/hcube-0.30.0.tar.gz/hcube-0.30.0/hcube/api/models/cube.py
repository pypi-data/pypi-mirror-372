from collections import OrderedDict, namedtuple
from typing import Type

from hcube.api.exceptions import ConfigurationError
from hcube.api.models.dimensions import Dimension
from hcube.api.models.metrics import Metric
from hcube.api.models.query import CubeQuery


class CubeMeta(type):
    def __new__(cls, *args, **kwargs):
        new_cls = super().__new__(cls, *args, **kwargs)
        new_cls._process_attrs()
        return new_cls

    def _process_attrs(cls):
        cls._dimensions = OrderedDict()
        cls._metrics = OrderedDict()
        cls._materialized_views = []
        for name in dir(cls):
            attr = getattr(cls, name)
            if isinstance(attr, Dimension):
                cls._dimensions[name] = attr
                if not attr.name:
                    attr.name = name
                attr.cube = cls
            elif isinstance(attr, Metric):
                cls._metrics[name] = attr
                if not attr.name:
                    attr.name = name


class Cube(metaclass=CubeMeta):
    @classmethod
    def record_type(cls):
        """
        Creates a `namedtuple` instance for record types of this cube
        :return:
        """
        return namedtuple(
            cls.__name__ + "Record",
            list(cls._dimensions.keys()) + list(cls._metrics.keys()),
        )

    @classmethod
    def cleanup_records(cls, records: [namedtuple]) -> [namedtuple]:
        """
        Applies dimension specific cleanup/conversion to each record in records
        """
        record_type = cls.record_type()
        return [cls.cleanup_record(record_type, record) for record in records]

    @classmethod
    def cleanup_record(cls, record_type: Type[namedtuple], record: namedtuple) -> namedtuple:
        """
        Applies dimension specific cleanup/conversion to each record in records. `record_type`
        is the named tuple that should be used for the output. It is not created in here as
        it would be costly to create it for individual records.
        """
        clean_data = {}
        for dim in cls._dimensions.values():
            clean_data[dim.name] = dim.to_python(getattr(record, dim.name))
        for metric in cls._metrics.values():
            clean_data[metric.name] = metric.to_python(getattr(record, metric.name))
        return record_type(**clean_data)

    @classmethod
    def query(cls):
        return CubeQuery(cls)

    @classmethod
    def dimension_by_name(cls, name: str) -> Dimension:
        try:
            return cls._dimensions[name]
        except KeyError:
            raise ConfigurationError(f"Unknown dimension: {name}") from None

    @classmethod
    def metric_by_name(cls, name: str) -> Metric:
        try:
            return cls._metrics[name]
        except KeyError:
            raise ConfigurationError(f"Unknown metric: {name}") from None

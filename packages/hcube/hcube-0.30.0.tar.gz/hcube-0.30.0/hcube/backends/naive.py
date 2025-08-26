from collections import namedtuple
from typing import Iterable, Iterator, NamedTuple, Type, Union

from hcube.api.backend import CubeBackend
from hcube.api.models.aggregation import AggregationOp, ArrayAgg, Count
from hcube.api.models.cube import Cube
from hcube.api.models.filters import (
    ComparisonFilter,
    ComparisonType,
    EqualityFilter,
    Filter,
    IsNullFilter,
    ListFilter,
    NegativeListFilter,
    Or,
    OverlapFilter,
    SubstringFilter,
    SubstringMultiValueFilter,
)
from hcube.api.models.group_filters import ComparisonGroupFilter, GroupFilter
from hcube.api.models.ordering import OrderDirection, OrderSpec
from hcube.api.models.query import CubeQuery
from hcube.api.models.transforms import ExplicitMappingTransform
from hcube.settings import GlobalSettings


class NaiveCubeBackend(CubeBackend):
    """
    Naive pure-python list based Cube backend.

    It is meant as an example and documentation and not for any serious work.
    """

    def __init__(self):
        self.values = []
        self._aggreg_state = {}

    def initialize_storage(self, cube: Type[Cube]) -> None:
        pass

    def drop_storage(self, cube: Type[Cube]) -> None:
        pass

    def store_records(self, cube: Type[Cube], records: Iterable[NamedTuple]):
        self.values = list(cube.cleanup_records(records))

    def get_records(self, query: CubeQuery) -> Iterator[NamedTuple]:
        aggreg_base = {agg.name: self._base_value(agg.op) for agg in query.aggregations}
        result = {}
        # if no groups or aggregations were defined, we are dealing with all dimensions
        if query.groups or query.aggregations:
            fields = query.groups
        else:
            fields = list(query.cube._dimensions.values()) + list(query.cube._metrics.values())
        for record in self.values:
            key = tuple(getattr(record, group.name) for group in fields)
            if not all(self._row_passes_filter(record, fltr) for fltr in query.filters):
                continue
            if key not in result:
                result[key] = {**aggreg_base}
            for agg in query.aggregations:
                if isinstance(agg, Count) and agg.distinct:
                    value = getattr(record, agg.distinct.name)
                    result[key][agg.name] = self._count_distinct(agg.name, value)
                elif isinstance(agg, ArrayAgg) and agg.distinct:
                    value = getattr(record, agg.distinct.name)
                    result[key][agg.name] = self._array_agg_distinct(agg.name, value)
                else:
                    if agg.filters:
                        if not all(self._row_passes_filter(record, fltr) for fltr in agg.filters):
                            continue
                    value = getattr(record, agg.dim_or_metric.name) if agg.dim_or_metric else None
                    result[key][agg.name] = self._aggregate(agg.op, result[key][agg.name], value)
            for transform in query.transforms:
                base_value = getattr(record, transform.dimension.name)
                if isinstance(transform, ExplicitMappingTransform):
                    result[key][transform.name] = transform.mapping.get(base_value, base_value)
                else:
                    raise ValueError(
                        f"Transformation {transform.__class__} is not supported by this backend"
                    )
        typ = namedtuple(
            "AggRecord",
            [grp.name for grp in fields]
            + [agg.name for agg in query.aggregations]
            + [tr.name for tr in query.transforms],
        )
        ret = [typ(*key, **aggs) for key, aggs in result.items()]
        # group filters
        if query.group_filters:
            ret = [
                record
                for record in ret
                if all(self._row_passes_filter(record, fltr) for fltr in query.group_filters)
            ]

        for sorter in reversed(query.orderings):
            # we assume sorting is stable, so sorting from the least important dimension will be
            # preserved in the result
            ret.sort(
                key=lambda x: self._sort_key(x, sorter),
                reverse=sorter.direction == OrderDirection.DESC,
            )
        # ensure there is at least one record if aggregations were applied and no group filters
        if not ret and query.aggregations and not query.group_filters:
            ret = [typ(**{agg.name: self._empty_value(agg.op) for agg in query.aggregations})]
        # limit
        if query.limit or query.offset:
            slc = slice(query.offset, ((query.offset or 0) + query.limit) if query.limit else None)
            ret = ret[slc]
        return ret

    def get_count(self, query: CubeQuery) -> int:
        return len(list(self.get_records(query)))

    def delete_records(self, query: CubeQuery) -> None:
        new_records = []
        for record in self.values:
            if not all(self._row_passes_filter(record, fltr) for fltr in query.filters):
                new_records.append(record)
        self.values = new_records

    @classmethod
    def _sort_key(cls, record, sorter: OrderSpec):
        value = getattr(record, sorter.dimension.name)
        if value is None:
            # sort nulls last - use 1 as first value
            return 1, sorter.dimension.default
        return 0, value

    @classmethod
    def _row_passes_filter(cls, row, fltr: Union[Filter, GroupFilter]) -> bool:
        # combinators first
        if isinstance(fltr, Or):
            return any(cls._row_passes_filter(row, subfltr) for subfltr in fltr.filters)
        # then plain filters
        value = getattr(row, fltr.dimension.name if isinstance(fltr, Filter) else fltr.agg.name)
        if isinstance(fltr, ListFilter):
            return value in fltr.values
        if isinstance(fltr, NegativeListFilter):
            return value not in fltr.values
        if isinstance(fltr, IsNullFilter):
            return (value is None) == fltr.is_null
        if isinstance(fltr, (ComparisonFilter, ComparisonGroupFilter)):
            if fltr.comparison == ComparisonType.GT:
                return value > fltr.value
            if fltr.comparison == ComparisonType.GTE:
                return value >= fltr.value
            if fltr.comparison == ComparisonType.LT:
                return value < fltr.value
            if fltr.comparison == ComparisonType.LTE:
                return value <= fltr.value
        if isinstance(fltr, EqualityFilter):
            return value == fltr.dimension.to_python(fltr.value)
        if isinstance(fltr, SubstringFilter):
            if fltr.case_sensitive:
                return fltr.value in value
            else:
                return fltr.value.lower() in value.lower()
        if isinstance(fltr, SubstringMultiValueFilter):
            if fltr.case_sensitive:
                return any(v in value for v in fltr.values)
            else:
                return any(v.lower() in value.lower() for v in fltr.values)
        if isinstance(fltr, OverlapFilter):
            return any(v in fltr.values for v in value)
        raise ValueError(f"unsupported filter {fltr}")

    @classmethod
    def _aggregate(cls, op: AggregationOp, base, value):
        if op == AggregationOp.COUNT:
            return base + 1
        elif op == AggregationOp.SUM:
            return base + value
        elif op == AggregationOp.MIN:
            return min(base, value) if base is not None else value
        elif op == AggregationOp.MAX:
            return max(base, value) if base is not None else value
        elif op == AggregationOp.ARRAY:
            return base + [value]
        else:
            raise ValueError(f"unsupported aggregation {op}")

    def _count_distinct(self, name, value):
        if name not in self._aggreg_state:
            self._aggreg_state[name] = set()
        self._aggreg_state[name].add(value)
        return len(self._aggreg_state[name])

    def _array_agg_distinct(self, name, value):
        if name not in self._aggreg_state:
            self._aggreg_state[name] = set()
        self._aggreg_state[name].add(value)
        return list(self._aggreg_state[name])

    @classmethod
    def _base_value(cls, op: AggregationOp):
        if op in (AggregationOp.COUNT, AggregationOp.SUM):
            return 0
        if op == AggregationOp.ARRAY:
            return []
        return None

    @classmethod
    def _empty_value(cls, op: AggregationOp):
        if op in (AggregationOp.COUNT,):
            return 0
        return 0 if GlobalSettings.aggregates_zero_for_empty_data else None

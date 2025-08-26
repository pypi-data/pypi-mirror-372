from typing import Any

from hcube.api.models.aggregation import Aggregation
from hcube.api.models.filters import ComparisonType


class GroupFilter:
    def __init__(self, agg: Aggregation):
        self.agg = agg


class ComparisonGroupFilter(GroupFilter):
    def __init__(self, agg: Aggregation, comparison: ComparisonType, value: Any):
        super().__init__(agg)
        self.comparison = comparison
        self.value = value

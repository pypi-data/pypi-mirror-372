from enum import Enum
from typing import Any, List, Optional, Set, Union

from hcube.api.models.dimensions import ArrayDimension, Dimension
from hcube.api.models.transforms import Transform


class Filter:
    def __init__(
        self, dimension: Union[Dimension, str], extra: Optional[dict] = None
    ):  # str will be resolved in query
        self.dimension = dimension
        self.extra = extra or {}

    def __str__(self):
        return f"{self.dimension}"

    def get_extra_param(self, key: str, default: Optional[Any] = None) -> Any:
        return self.extra.get(key, default)


class EqualityFilter(Filter):
    def __init__(
        self, dimension: Union[Dimension, str], value: Union[str, int], extra: Optional[dict] = None
    ):
        super().__init__(dimension, extra=extra)
        self.value = value

    def __str__(self):
        return f"{self.dimension}={self.value}"


class ListFilter(Filter):
    def __init__(
        self, dimension: Union[Dimension, str], values: list, extra: Optional[dict] = None
    ):
        super().__init__(dimension, extra=extra)
        self.values = values

    def __str__(self):
        return f"{self.dimension} in {self.values}"


class NegativeListFilter(Filter):
    def __init__(
        self, dimension: Union[Dimension, str], values: list, extra: Optional[dict] = None
    ):
        super().__init__(dimension, extra=extra)
        self.values = values

    def __str__(self):
        return f"{self.dimension} not in {self.values}"


class IsNullFilter(Filter):
    def __init__(
        self, dimension: Union[Dimension, str], is_null: bool, extra: Optional[dict] = None
    ):
        super().__init__(dimension, extra=extra)
        self.is_null = is_null

    def __str__(self):
        return f"{self.dimension} is {'NULL' if self.is_null else 'NOT NULL'}"


class ComparisonType(Enum):
    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="


class ComparisonFilter(Filter):
    def __init__(
        self,
        dimension: Union[Dimension, str],
        comparison: ComparisonType,
        value: Any,
        extra: Optional[dict] = None,
    ):
        super().__init__(dimension, extra=extra)
        self.comparison = comparison
        self.value = value

    def __str__(self):
        return f"{self.dimension} {self.comparison.value} {self.value}"


class SubstringFilter(Filter):
    def __init__(
        self,
        dimension: Union[Dimension, str],
        value: str,
        case_sensitive: bool = True,
        extra: Optional[dict] = None,
    ):
        super().__init__(dimension, extra=extra)
        self.value = value
        self.case_sensitive = case_sensitive

    def __str__(self):
        return f"{self.dimension} contains '{self.value}'"


class SubstringMultiValueFilter(Filter):
    """
    Represents matching a value against a list of values. If any value matches, the filter matches.
    """

    def __init__(
        self,
        dimension: Union[Dimension, str],
        values: [str],
        case_sensitive: bool = True,
        extra: Optional[dict] = None,
    ):
        super().__init__(dimension, extra=extra)
        self.values = list(values)
        self.case_sensitive = case_sensitive

    def __str__(self):
        return f"{self.dimension} contains any of {self.values}"


class OverlapFilter(Filter):
    """
    Describes overlap between two arrays.
    """

    def __init__(
        self, dimension: Union[Dimension, str], values: list, extra: Optional[dict] = None
    ):
        if not isinstance(dimension, (ArrayDimension, Transform)):
            raise ValueError(
                "OverlapFilter can only be used with ArrayDimension or a Transform, "
                "'{}' given".format(dimension)
            )
        super().__init__(dimension, extra=extra)
        self.values = list(values)

    def __str__(self):
        return f"{self.dimension} overlaps with {self.values}"


class Wrapper:
    """
    This is helper class wrapping one filter shorthand. It is similar to Django Q objects,
    but only limited to one filter.
    """

    def __init__(self, **named_filters):
        if len(named_filters) > 1:
            raise ValueError("Wrapper can only wrap one filter")
        for key, value in named_filters.items():
            self.key = key
            self.value = value


class FilterCombinator:
    def __init__(self, *filters: Union[Filter, Wrapper], extra: Optional[dict] = None):
        self.filters: List[Filter] = list(filters)
        self.extra = extra or {}

    def get_extra_param(self, key: str, default: Optional[Any] = None) -> Any:
        return self.extra.get(key, default)

    def get_involved_dimensions(self) -> Set[Dimension]:
        """
        Recursively walks through the filters and returns all dimensions involved in the filters.
        """
        out = set()
        for fltr in self.filters:
            if isinstance(fltr, FilterCombinator):
                out |= fltr.get_involved_dimensions()
            else:
                out.add(fltr.dimension)
        return out


class Or(FilterCombinator):
    def __str__(self):
        return " OR ".join(str(fltr) for fltr in self.filters)

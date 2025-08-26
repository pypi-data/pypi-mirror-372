"""
Functionality to transform data obtained from the database. Equivalent to applying a function on
some of the rows.

Not all backends need to support all transforms.
"""

from enum import Enum
from typing import Any, List, Optional, Union

from hcube.api.models.dimensions import Dimension


class Transform:
    """
    `dimension` is the dimension to be transformed.
    `name` is the field name under which the resulting value will appear
    """

    def __init__(self, dimension: Optional[Union[Dimension, str]], name: Optional[str] = None):
        self.dimension = dimension
        dim_name = dimension.name if isinstance(dimension, Dimension) else dimension
        self.name = name if name else dim_name


class StoredMappingTransform(Transform):
    """
    This transform assumes that there is a mapping with `mapping_name` stored at the backend.
    The mapping may be multidimensional, so `mapping_field` is used to select the appropriate
    'row' from the mapping.
    """

    def __init__(
        self,
        dimension: Union[Dimension, str],
        mapping_name: str,
        mapping_field: Optional[str],
        name: Optional[str] = None,
    ):
        super().__init__(dimension, name=name)
        self.mapping_name = mapping_name
        self.mapping_field = mapping_field


StoredMap = StoredMappingTransform


class ExplicitMappingTransform(Transform):
    """
    This transform expects a dict-like mapping to be given as one of the params and then uses
    this mapping to convert values of `dimension` to the resulting values.
    """

    def __init__(
        self,
        dimension: Union[Dimension, str],
        mapping: dict,
        default: Optional[Any] = None,
        name: Optional[str] = None,
    ):
        super().__init__(dimension, name)
        self.mapping = mapping
        self.default = default


# just an alias for simpler name
Map = ExplicitMappingTransform


class IdentityTransform(Transform):
    """
    This transform is a no-op. It just returns the value of the dimension as is. The main purpose
    is to rename one dimension to another.
    """

    def __init__(self, dimension: Union[Dimension, str], name: Optional[str] = None):
        super().__init__(dimension, name)


IdentityMap = IdentityTransform


class VerbatimTransform(Transform):
    """
    The text of the transform is applied verbatim to the query. This is useful to pass some
    backend-specific functions which would be hard to implement in a generic way.

    The `dimension` is not used, so it is set to None.

    However, we may still benefit from knowing which dimensions (if any) are involved in the
    transform, because we can use it to determine which materialized views to use.
    If `involved_dimensions` is set to None, it is assumed that all dimensions are involved
    in the transform, so no materialized views can be used.
    If `involved_dimensions` is an empty list, it is assumed that no dimensions are involved in
    the transform, so this transform is safe to use with any materialized view.
    If `involved_dimensions` is a list of dimensions, these dimensions are used to determine
    which materialized views can be used.
    """

    def __init__(
        self,
        text: str,
        name: Optional[str] = None,
        involved_dimensions: Optional[List[Dimension]] = None,
    ):
        super().__init__(None, name)
        self.text = text
        self.involved_dimensions = involved_dimensions


RawMap = VerbatimTransform


class FunctionTransform(Transform):
    """
    This transform applies a function to the value of the dimension.
    The name of the function is applied verbatim to the query, so it is backend-specific.
    """

    def __init__(self, dimension: Union[Dimension, str], function: str, name: Optional[str] = None):
        super().__init__(dimension, name)
        self.function = function


FuncMap = FunctionTransform


class JoinType(Enum):
    INNER = "inner"
    LEFT = "left"
    RIGHT = "right"
    FULL = "full"


class JoinTransform(Transform):
    """
    This transform joins another table to the main table.
    """

    def __init__(
        self,
        dimension: Union[Dimension, str],  # dimension to be joined
        joined_dim: Dimension,  # dimension in the joined table on which to join
        target_dim: Dimension,  # dimension in the joined table which is result of the transform
        join_type: JoinType = JoinType.LEFT,  # type of join
        name: Optional[str] = None,
        join_filters: Optional[list] = None,  # filters to be applied to the join condition
    ):
        super().__init__(dimension, name)
        self.joined_dim = joined_dim
        self.target_dim = target_dim
        self.join_type = join_type
        self.join_filters = join_filters or []
        if not isinstance(self.join_type, JoinType):
            raise ValueError(f"Invalid join type: '{join_type}'")
        if self.joined_dim.cube is not self.target_dim.cube:
            raise ValueError("Joined dimension and target dimension must be from the same cube")


JoinMap = JoinTransform

"""
Injections allow for adding data to a query result in some way.
"""

from typing import TYPE_CHECKING, List, Optional

from hcube.api.models.dimensions import Dimension

if TYPE_CHECKING:
    from hcube.api.models.query import CubeQuery


class Injection:
    pass


class GroupValuesInjection(Injection):
    """
    Makes it possible to supply a list of values to be used as source of all the groups that
    should be returned by a query. This is useful when the groups are not present in the data
    and there is an external source of the groups.
    """

    def __init__(self, group_by: List[Dimension]):
        self.group_by = group_by


class DictionaryGroupValuesInjection(GroupValuesInjection):
    """
    GroupValuesInjection that uses a dictionary to supply the groups.
    """

    def __init__(
        self,
        group_by: List[Dimension],
        dictionary_name: str,
        dictionary_keys: Optional[List[str]] = None,
    ):
        super().__init__(group_by)
        self.dictionary_name = dictionary_name
        self.dictionary_keys = dictionary_keys or [g for g in group_by]

    def groups_and_keys(self):
        return list(zip(self.group_by, self.dictionary_keys))


class QueryGroupValuesInjection(GroupValuesInjection):
    """
    GroupValuesInjection that uses a query to supply the groups.
    """

    def __init__(self, group_by: List[Dimension], query: "CubeQuery"):
        super().__init__(group_by)
        self.query = query

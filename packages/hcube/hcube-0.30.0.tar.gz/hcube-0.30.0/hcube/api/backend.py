import abc
from typing import Iterable, Iterator, NamedTuple, Type

from hcube.api.models.cube import Cube
from hcube.api.models.query import CubeQuery


class CubeBackend(abc.ABC):
    @abc.abstractmethod
    def get_records(self, query: CubeQuery) -> Iterator[NamedTuple]:
        """
        Takes a `CubeQuery` instance and returns the resulting records
        """

    def get_one_record(self, query: CubeQuery) -> NamedTuple:
        """
        A convenience method for situations where only one record is returned by a query
        (usually result of aggregation over the whole set)
        """
        return list(self.get_records(query))[0]

    @abc.abstractmethod
    def get_count(self, query: CubeQuery) -> int:
        """
        Returns the number of records returned by a query
        """

    @abc.abstractmethod
    def store_records(self, cube: Type[Cube], records: Iterable[NamedTuple]):
        """
        Stores `records` for `cube` in the backing storage
        """

    @abc.abstractmethod
    def delete_records(self, query: CubeQuery) -> None:
        """
        Takes a `CubeQuery` instance and removes all matching records
        """

    @abc.abstractmethod
    def initialize_storage(self, cube: Type[Cube]) -> None:
        """
        Initializes the backing storage for `cube` - creates a table, etc.
        """

    @abc.abstractmethod
    def drop_storage(self, cube: Type[Cube]) -> None:
        """
        Drops the backing storage for `cube` - drops a table, etc.
        """

import logging
from collections import namedtuple
from ipaddress import IPv4Address, IPv6Address
from typing import Iterable, Iterator, NamedTuple, Optional, Type, Union

import psycopg2
from decouple import config
from psycopg2.extras import Json

from hcube.api.backend import CubeBackend
from hcube.api.exceptions import ConfigurationError
from hcube.api.models.aggregation import AggregationOp, ArrayAgg, Count
from hcube.api.models.cube import Cube
from hcube.api.models.dimensions import (
    ArrayDimension,
    BooleanDimension,
    DateDimension,
    DateTimeDimension,
    Dimension,
    IntDimension,
    IPDimension,
    MapDimension,
    StringDimension,
)
from hcube.api.models.filters import (
    ComparisonFilter,
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
from hcube.api.models.metrics import FloatMetric, IntMetric, Metric
from hcube.api.models.query import CubeQuery
from hcube.settings import GlobalSettings

logger = logging.getLogger(__name__)


def db_params_from_env(test=False):
    test_conf = "_TEST" if test else ""
    host = config(f"POSTGRES_HOST{test_conf}", "localhost")
    database = config(f"POSTGRES_DB{test_conf}", "test" if test else None)
    user = config(f"POSTGRES_USER{test_conf}", "hcube" if test else None)
    password = config(f"POSTGRES_PASSWORD{test_conf}", None)
    schema = config(f"POSTGRES_SCHEMA{test_conf}", "public")
    out = {"host": host, "schema": schema}
    # we do not want to add the keys if the values are None so that the client can use default
    # values
    if database is not None:
        out["database"] = database
    if user is not None:
        out["user"] = user
    if password is not None:
        out["password"] = password
    return out


class PostgresCubeBackend(CubeBackend):
    """
    Backend to Postgres using the low-level Postgres API from `psycopg2`.
    """

    dimension_type_map = (
        (IntDimension, "Integer"),
        (StringDimension, "Text"),
        (DateDimension, "Date"),
        (DateTimeDimension, "Timestamp"),
        (FloatMetric, "Float"),
        (IntMetric, "Integer"),
        (IPDimension, "Inet"),
        (BooleanDimension, "Boolean"),
    )

    def __init__(
        self,
        schema="public",
        database=None,
        **client_attrs,
    ):
        super().__init__()
        self.database = database
        assert self.database, "database must be present"
        self.client_attrs = client_attrs
        self.connection = psycopg2.connect(database=database, **client_attrs)
        self.schema = schema

    def initialize_storage(self, cube: Type[Cube]) -> None:
        self._init_table(cube)

    def drop_storage(self, cube: Type[Cube]) -> None:
        self._execute(f"DROP TABLE {self.schema}.{self.cube_to_table_name(cube)};")

    def store_records(self, cube: Type[Cube], records: Iterable[NamedTuple]):
        clean_records = cube.cleanup_records(records)
        values_part = ", ".join(f"%({field})s" for field in cube.record_type()._fields)
        self._execute(
            f"INSERT INTO {self.schema}.{self.cube_to_table_name(cube)} VALUES ({values_part});",
            [{**self._to_sql_dict(rec)} for rec in clean_records],
            exec_many=True,
        )

    @classmethod
    def _to_sql_dict(cls, rec):
        ret = {}
        for field, value in rec._asdict().items():
            if type(value) is dict:  # noqa E721
                ret[field] = Json(value)
            elif isinstance(value, (IPv4Address, IPv6Address)):
                ret[field] = str(value)
            else:
                ret[field] = value
        return ret

    def get_records(self, query: CubeQuery) -> Iterator[NamedTuple]:
        text, params, fields = self._prepare_db_query(query)
        logger.debug('Query: "%s", params: "%s"', text, params)
        result = namedtuple("Result", fields)
        output = self._execute(text, params, fetch="all")
        for rec in output:
            yield result(*rec)

    def get_count(self, query: CubeQuery) -> int:
        text, params, _fields = self._prepare_db_query(query)
        text = f"SELECT COUNT(*) FROM ({text}) AS _count"
        logger.debug('Query: "%s", params: "%s"', text, params)
        output = self._execute(text, params, fetch="one")
        return output[0]

    def delete_records(self, query: CubeQuery) -> None:
        # check that the query can be used
        if (
            query.aggregations
            or query.groups
            or query.transforms
            or query.orderings
            or query.limit
            or query.offset
        ):
            raise ConfigurationError(
                "Delete query can only have a filter, no aggregations, group_bys, ordering, limit,"
                "offset or transforms"
            )
        query_parts = {}
        # we run it just for the parts and params
        _text, params, _fields = self._prepare_db_query(query, parts=query_parts)
        if where := query_parts["where"]:
            text = f"DELETE FROM {query_parts['table']} WHERE {where}"
        else:
            text = f"DELETE FROM {query_parts['table']}"
        self._execute(text, params)

    def _get_cursor(self):
        return self.connection.cursor()

    def _execute(self, *params, exec_many=False, fetch=None):
        with self.connection.cursor() as cursor:
            if exec_many:
                cursor.executemany(*params)
            else:
                cursor.execute(*params)
            self.connection.commit()
            if fetch == "all":
                return cursor.fetchall()
            elif fetch == "one":
                return cursor.fetchone()

    def _prepare_db_query(
        self, query: CubeQuery, parts: Optional[dict] = None
    ) -> (str, dict, list):
        """
        returns the query text, parameters to be added during execution and a list of parameter
        names that are expected in the result
        """
        params = {}
        if query.groups or query.aggregations:
            fields = [grp.name for grp in query.groups]
            select_parts = [*fields]
            for agg in query.aggregations:
                agg_name = self._agg_name(agg.op)
                inside = "*"
                if agg.dim_or_metric:
                    inside = agg.dim_or_metric.name
                elif isinstance(agg, (Count, ArrayAgg)) and agg.distinct:
                    inside = f"DISTINCT {agg.distinct.name}"
                # filters
                filter_parts = []
                filter_text = ""
                for filtr in agg.filters:
                    text, agg_params = self._pg_filter(filtr)
                    filter_parts.append(text)
                    params.update(agg_params)
                if filter_parts:
                    filter_text = "FILTER (WHERE " + " AND ".join(filter_parts) + ")"
                # over
                over = "" if not agg.over_all else "OVER ()"
                # coalescing
                if GlobalSettings.aggregates_zero_for_empty_data:
                    select_parts.append(
                        f"COALESCE({agg_name}({inside}) {filter_text}, 0) {over} AS {agg.name}"
                    )
                else:
                    select_parts.append(f"{agg_name}({inside}) {filter_text} {over} AS {agg.name}")
                fields.append(agg.name)
        else:
            fields = [dim.name for dim in query.cube._dimensions.values()] + [
                metric.name for metric in query.cube._metrics.values()
            ]
            select_parts = fields[:]
        # group aggregations
        having_parts = []
        for gf in query.group_filters:
            inside = "*"
            if gf.agg.dim_or_metric:
                inside = gf.agg.dim_or_metric.name
            fn_name = self._agg_name(gf.agg.op)
            having_parts.append(f"{fn_name}({inside}) {gf.comparison.value} {gf.value}")
        select = ", ".join(select_parts)
        group_by = ", ".join(grp.name for grp in query.groups)
        table = f"{self.schema}.{self.cube_to_table_name(query.cube)}"
        order_by = ", ".join(f"{ob.dimension.name} {ob.direction.name}" for ob in query.orderings)
        where_parts = []
        for fltr in query.filters:
            filter_text, filter_params = self._pg_filter(fltr)
            where_parts.append(filter_text)
            params.update(filter_params)
        where = " AND ".join(where_parts)
        # put it together
        text = f"SELECT {select} FROM {table} "
        if where:
            text += f"WHERE {where} "
        if group_by:
            text += f"GROUP BY {group_by} "
        if having_parts:
            text += f"HAVING {' AND '.join(having_parts)} "
        if order_by:
            text += f"ORDER BY {order_by} "
        if query.limit:
            text += f"LIMIT {query.limit} "
        if query.offset:
            text += f"OFFSET {query.offset} "
        if isinstance(parts, dict):
            parts.update(
                {
                    "table": table,
                    "select": select,
                    "where": where,
                    "group_by": group_by,
                    "order_by": order_by,
                    "limit": query.limit,
                }
            )
        return text, params, fields

    def _pg_filter(self, fltr: Filter) -> (str, dict):
        """
        returns a tuple with the string that should be put into the where part of the query and
        a dictionary with the parameters that should be passed to the query during execution
        for proper escaping.
        """
        # combinators first
        if isinstance(fltr, Or):
            queries = []
            params = {}
            for subfilter in fltr.filters:
                query, subparams = self._pg_filter(subfilter)
                queries.append(query)
                params.update(subparams)
            return " OR ".join(queries), params
        # then plain filters
        # add id(fltr) to the name because there may be more than one filter for the same dimension
        key = f"_where_{id(fltr)}_{fltr.dimension.name}"
        if isinstance(fltr, ListFilter):
            return f"{fltr.dimension.name} IN %({key})s", {key: tuple(fltr.values)}
        if isinstance(fltr, NegativeListFilter):
            return f"{fltr.dimension.name} NOT IN %({key})s", {key: tuple(fltr.values)}
        if isinstance(fltr, IsNullFilter):
            modifier = "" if fltr.is_null else " NOT"
            return f"{fltr.dimension.name} IS{modifier} NULL", {}
        if isinstance(fltr, ComparisonFilter):
            return f"{fltr.dimension.name} {fltr.comparison.value} %({key})s", {key: fltr.value}
        if isinstance(fltr, EqualityFilter):
            return f"{fltr.dimension.name} = %({key})s", {key: fltr.value}
        if isinstance(fltr, SubstringFilter):
            op = "LIKE" if fltr.case_sensitive else "ILIKE"
            return f"{fltr.dimension.name} {op} %({key})s", {key: f"%{fltr.value}%"}
        if isinstance(fltr, SubstringMultiValueFilter):
            op = "LIKE" if fltr.case_sensitive else "ILIKE"
            return " OR ".join(
                f"{fltr.dimension.name} {op} %({key}_{i})s" for i in range(len(fltr.values))
            ), {f"{key}_{i}": f"%{value}%" for i, value in enumerate(fltr.values)}
        if isinstance(fltr, OverlapFilter):
            return f"{fltr.dimension.name} && %({key})s", {key: fltr.values}
        raise ValueError(f"unsupported filter {fltr.__class__}")

    def _agg_name(self, agg: AggregationOp):
        if agg in (
            AggregationOp.SUM,
            AggregationOp.COUNT,
            AggregationOp.MAX,
            AggregationOp.MIN,
        ):
            return agg.name
        if agg == AggregationOp.ARRAY:
            return "ARRAY_AGG"
        raise ValueError(f"Unsupported aggregation {agg}")

    @staticmethod
    def cube_to_table_name(cube: Type[Cube]):
        return cube.__name__.lower()

    def _init_table(self, cube: Type[Cube]):
        """
        Creates the corresponding db table if the table is not yet present.
        """
        name = self.cube_to_table_name(cube)
        fields = [
            f"{dim.name} {self._ch_type(dim)}"
            for dim in list(cube._dimensions.values()) + list(cube._metrics.values())
        ]
        field_part = ", ".join(fields)
        command = f"CREATE TABLE IF NOT EXISTS {self.schema}.{name} ({field_part})"
        logger.debug(command)
        self._execute(command)

    def _ch_type(self, dimension: Union[Dimension, Metric]) -> str:
        a, b = self._ch_type_parts(dimension)
        return f"{a} {b}" if b else a

    def _ch_type_parts(self, dimension: Union[Dimension, Metric]) -> (str, str):
        if isinstance(dimension, ArrayDimension):
            subtype, _subnull = self._ch_type_parts(dimension.dimension)
            # we ignore the null definition
            return f"{subtype}[]", ""
        if isinstance(dimension, MapDimension):
            keyb_subtype, _subnull = self._ch_type_parts(dimension.key_dimension)
            value_subtype, _subnull = self._ch_type_parts(dimension.value_dimension)
            # we ignore the null definition
            return "jsonb", ""
        for dim_cls, ch_type in self.dimension_type_map:
            if isinstance(dimension, dim_cls):
                if hasattr(dimension, "null") and dimension.null:
                    return ch_type, ""
                return ch_type, "NOT NULL"
        raise ValueError("unsupported dimension: %s", dimension.__class__)

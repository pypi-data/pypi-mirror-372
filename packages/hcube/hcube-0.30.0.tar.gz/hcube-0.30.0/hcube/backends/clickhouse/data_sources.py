import abc


class DataSource(abc.ABC):
    """
    Generic data source for connecting extrenal data sources to clickhouse.
    """

    @abc.abstractmethod
    def __init__(self):
        pass

    @abc.abstractmethod
    def definition_sql(self) -> str:
        """
        Returns the SQL definition of the data source.
        """

    @abc.abstractmethod
    def engine_definition_sql(self) -> str:
        """
        Returns the SQL definition of the engine for the data source.
        Useful when getting a foreign table (for example PostgreSQL) into Clickhouse.
        """


class PostgresqlSource(DataSource):
    def __init__(
        self,
        database,
        table=None,
        query=None,
        host="localhost",
        port=5432,
        user="postgres",
        password="",
        invalidate_query=None,
    ):
        super().__init__()
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.table = table
        self.query = query
        self.invalidate_query = invalidate_query
        if not bool(self.table) ^ bool(self.query):
            raise ValueError("Either table or query must be specified, but not both.")

    def definition_sql(self):
        invalidate_query = ""
        if self.invalidate_query:
            invalidate_query = f"invalidate_query '{self.invalidate_query}'"
        # self.table and self.query are mutually exclusive, which is already enforced in
        # the constructor, so we can rely on the fact that only one of them is set.
        table_part = f"table '{self.table}'" if self.table else f"query '{self.query}'"
        return f"""SOURCE(POSTGRESQL(
            port {self.port}
            host '{self.host}'
            user '{self.user}'
            password '{self.password}'
            db '{self.database}'
            {table_part}
            {invalidate_query}
        ))"""

    def engine_definition_sql(self):
        return (
            f"PostgreSQL('{self.host}:{self.port}', '{self.database}', '{self.table}', "
            f"'{self.user}', '{self.password}');"
        )


class ClickhouseSource(DataSource):
    def __init__(
        self,
        database,
        table,
        host="localhost",
        port=9000,
        user="default",
        password="",
        secure=False,
    ):
        super().__init__()
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.table = table
        self.secure = secure

    def definition_sql(self):
        return f"""SOURCE(CLICKHOUSE(
            port {self.port}
            host '{self.host}'
            user '{self.user}'
            password '{self.password}'
            db '{self.database}'
            table '{self.table}'
            secure {1 if self.secure else 0}
        ))"""

    def engine_definition_sql(self):
        # as of 2024-04-08 there does not seem to be an external engine for Clickhouse,
        # so we just return an empty string to signalize that the engine is not needed.
        return ""

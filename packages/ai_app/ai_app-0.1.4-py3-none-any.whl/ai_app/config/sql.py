import enum
import functools
import os

import pydantic
import sqlalchemy as sa

from ai_app.utils import PydanticForbidExtra


class Driver(enum.StrEnum):
    oracle = enum.auto()
    postgresql = enum.auto()
    mssql = enum.auto()

    @property
    def name_and_package(self):
        match self:
            case Driver.oracle:
                return "oracle+oracledb"
            case Driver.postgresql:
                return "postgresql+psycopg"
            case Driver.mssql:
                return "mssql+pymssql"

        assert False


@functools.cache
def init_oracle_thick_mode():
    if path := os.getenv("ORACLE_INSTANT_CLIENT_LIB"):
        import oracledb

        oracledb.init_oracle_client(path)


class Connection(PydanticForbidExtra):
    driver: Driver
    host: str
    port: int
    database: str | None = None
    username: str
    password: str
    parameters: dict[str, str] = {}

    @property
    def url(self) -> sa.URL:
        url = sa.URL.create(
            drivername=self.driver.name_and_package,
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            database=self.database,
            query=self.parameters,
        )
        return url

    def build_engine(self, **kwargs) -> sa.Engine:
        # if self.driver == Driver.oracle:
        #     init_oracle_thick_mode()

        engine = sa.create_engine(self.url, **kwargs)
        return engine


class ConnectionContext(PydanticForbidExtra):
    connection_name: str
    schema_tables: list[str] = []

    @pydantic.model_validator(mode="after")
    def _validate(cls, self):
        self.get_tables_by_schema()
        return self

    def get_tables_by_schema(self) -> dict[str | None, list[str]]:
        tables_by_schema = {}
        for table in self.schema_tables:
            if "." in table:
                schema, table = table.split(".")
            else:
                schema = None

            tables_by_schema.setdefault(schema, []).append(table)

        return tables_by_schema

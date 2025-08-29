import contextlib
import logging
from typing import Iterable

import logfire
import numpy as np
import pgvector.sqlalchemy
import sqlalchemy as sa
import sqlmodel


@contextlib.contextmanager
def open_session(
    engine: sa.Engine,
    commit_on_exit: bool = False,
    use_autocommit_isolation_level: bool = False,
    logfire_span_name: str = "SQLModel session",
    **session_kwargs,
):
    if use_autocommit_isolation_level:
        engine = engine.execution_options(isolation_level="AUTOCOMMIT")

    with sqlmodel.Session(engine, **session_kwargs) as session, logfire.span(logfire_span_name):
        yield session
        if commit_on_exit:
            session.commit()


def execute_text_statements(engine: sa.Engine, commands: Iterable[str], **kwargs):
    for command in commands:
        with open_session(engine, commit_on_exit=True, **kwargs) as session:
            session.exec(sa.text(command))


def setup_pgvector(engine: sa.Engine):
    """Requires superuser permissions."""
    execute_text_statements(engine, ["CREATE EXTENSION IF NOT EXISTS vector"])


def create_vector_index(
    engine: sa.Engine,
    table_name: str,
    column_name: str = "embedding",
    index_type: str = "hnsw ({column_name} vector_cosine_ops)",
):
    index_type = index_type.format(column_name=column_name)
    statement = f"""
        CREATE INDEX CONCURRENTLY IF NOT EXISTS {table_name}_embedding_index
        ON {table_name}
        USING {index_type}
    """
    execute_text_statements(engine, [statement], use_autocommit_isolation_level=True)


def get_cosine_distance_embedding_sqlmodel_mixin(
    dimension: int, nullable: bool = False
) -> type[sqlmodel.SQLModel]:
    class CosineDistanceEmbeddingMixin(sqlmodel.SQLModel):
        embedding: list[float] | None if nullable else list[float] = sqlmodel.Field(
            sa_type=pgvector.sqlalchemy.Vector(dimension), nullable=nullable
        )

        @classmethod
        def create_vector_index(cls, engine: sa.Engine):
            create_vector_index(engine, cls.__tablename__)

        @classmethod
        def distance(cls, other: np.ndarray) -> sa.sql.elements.BinaryExpression:
            return cls.embedding.cosine_distance(other)

        @classmethod
        def nearest_neighbors(
            cls, select: sa.sql.Select, other: np.ndarray, limit: int
        ) -> sa.sql.Select:
            return select.order_by(cls.distance(other)).limit(limit)

    return CosineDistanceEmbeddingMixin


def user_exists(engine: sa.Engine, username: str) -> bool:
    """Check if a PostgreSQL user exists."""
    with engine.connect() as conn:
        statement = f"SELECT 1 FROM pg_roles WHERE rolname = '{username}'"
        result = conn.execute(sa.text(statement)).scalar()

    return bool(result)


def setup_user(engine: sa.Engine, user: str, password: str):
    if user_exists(engine, user):
        logging.info(f"User {user} already exists, skipping creation")
        return

    statements = f"""
        CREATE USER {user} WITH PASSWORD '{password}';

        GRANT USAGE ON SCHEMA public TO {user};
        GRANT CREATE ON SCHEMA public TO {user};

        GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO {user};

        GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO {user};

        ALTER DEFAULT PRIVILEGES IN SCHEMA public
        GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {user};

        ALTER DEFAULT PRIVILEGES IN SCHEMA public
        GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO {user};
    """
    execute_text_statements(engine, [statements])


def get_column_path(column: sa.Column, with_schema: bool = False) -> str:
    path = [column.table.name, column.name]
    if with_schema:
        path = [column.table.schema] + path

    path = ".".join(path)
    return path


def drop_all_tables(engine: sa.Engine):
    metadata = sa.MetaData()
    metadata.reflect(engine)
    metadata.drop_all(engine)


def build_foreign_key_constraint(
    sql_model: type[sqlmodel.SQLModel], ondelete: str | None = "CASCADE"
) -> sa.ForeignKeyConstraint:
    primary_keys = [c for c in sql_model.__table__.c if c.primary_key]
    columns = [c.name for c in primary_keys]
    refcolumns = [f"{c.table.name}.{c.name}" for c in primary_keys]
    constraint = sa.ForeignKeyConstraint(columns, refcolumns, ondelete=ondelete)
    return constraint


def create_index(
    engine: sa.Engine,
    table_name: str,
    columns: Iterable[str],
    schema: str | None = None,
    unique: bool = False,
):
    metadata = sa.MetaData(schema=schema)
    metadata.reflect(engine, only=[table_name])
    table = f"{schema}.{table_name}" if schema else table_name
    table = metadata.tables[table]
    with engine.connect() as connection:
        index = sa.Index(
            None,  # Index name.
            *(table.c[c] for c in columns),
            unique=unique,
        )
        index.create(connection, checkfirst=True)
        connection.commit()

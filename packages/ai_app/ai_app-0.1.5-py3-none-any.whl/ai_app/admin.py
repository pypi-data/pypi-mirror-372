import datetime
import itertools

import alembic.command
import polars as pl
import prefect

from ai_app.apps.jira_service_desk.preparation import (
    update_ai_jira_request_guides,
    update_jira_requests,
    update_manual_jira_requests,
)
from ai_app.config import (
    get_ai_postgres_engine,
    get_alembic_config,
    get_chat_model,
    get_config,
    get_engine,
    get_jira_service_desk_spreadsheets,
)
from ai_app.sql import setup_pgvector, setup_user


def initial_setup():
    admin_engine = get_engine("postgres_ai_admin")
    setup_pgvector(admin_engine)
    engine = get_ai_postgres_engine()
    setup_user(admin_engine, user=engine.url.username, password=engine.url.password)


def alembic_upgrade():
    alembic_config = get_alembic_config()
    alembic.command.upgrade(alembic_config, "head")


@prefect.task
def sync_dwh_tables(connection_schema_tables: dict[str, dict[str, list[str]]]):
    """Sync SQL tables from DWH to Postgres"""
    all_tables = list(
        itertools.chain(
            *(
                list(itertools.chain(*schema_tables.values()))
                for schema_tables in connection_schema_tables.values()
            )
        )
    )
    if len(all_tables) != len(set(all_tables)):
        raise ValueError("Table names are not unique")

    output_engine = get_engine("postgres_ai_dwh")
    for connection, schema_tables in connection_schema_tables.items():
        input_engine = get_engine(connection)
        for schema, tables in schema_tables.items():
            for table in tables:
                df = pl.read_database(
                    f"SELECT * from {schema}.{table}", input_engine, infer_schema_length=None
                )
                df.write_database(table, output_engine, if_table_exists="replace")


@prefect.flow
def update_jira_requests_meta_and_manual_data():
    get_config().setup_logging()
    prefect.task(update_jira_requests)()
    prefect.task(update_manual_jira_requests)(
        spreadsheets=get_jira_service_desk_spreadsheets(),
        write_back_to_gsheet=True,
    )


@prefect.flow
def update_ai_jira_request_summaries_and_embeddings():
    """
    Note that after adding new request types to AI Gsheet, they will have do_recommend=0,
    thus they will not be recommended to users until the field is manually set to 1.
    """
    get_config().setup_logging()
    prefect.task(update_ai_jira_request_guides)(
        model=get_chat_model("gpt-5-mini"),
        limit_requests=100,
    )


def main():
    prefect.serve(
        update_jira_requests_meta_and_manual_data.to_deployment(
            "update_jira_requests_meta_and_manual_data",
            interval=datetime.timedelta(hours=1),
            paused=True,
        ),
        update_ai_jira_request_summaries_and_embeddings.to_deployment(
            "update_ai_jira_request_summaries_and_embeddings",
            interval=datetime.timedelta(days=1),
            paused=True,
        ),
    )


if __name__ == "__main__":
    main()

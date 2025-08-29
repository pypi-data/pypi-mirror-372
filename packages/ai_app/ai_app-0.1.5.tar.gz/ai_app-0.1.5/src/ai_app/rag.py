from typing import Iterable

import langchain_openai
import langchain_postgres
import langchain_postgres.v2.indexes
import sqlalchemy as sa

from ai_app.sql import create_index


def build_postgres_vector_store(
    engine: sa.Engine,
    openai_api_key: str,
    table_name: str,
    metadata_columns: Iterable[langchain_postgres.Column] | None = None,
    ensure_metadata_columns_index_is_unique: bool = False,
    retrieved_document_count: int = 5,
    embedding_model: str = "text-embedding-3-small",
    vector_dimension: int = 1024,
    overwrite_existing_table: bool = False,
) -> langchain_postgres.PGVectorStore:
    pg_engine = langchain_postgres.PGEngine.from_connection_string(engine.url)
    embeddings = langchain_openai.OpenAIEmbeddings(
        model=embedding_model,
        dimensions=vector_dimension,
        api_key=openai_api_key,
    )
    vector_index = None
    metadata_columns_names = [c.name for c in metadata_columns]
    if overwrite_existing_table or not sa.inspect(engine).has_table(table_name):
        pg_engine.init_vectorstore_table(
            table_name=table_name,
            vector_size=vector_dimension,
            metadata_columns=metadata_columns,
            overwrite_existing=overwrite_existing_table,
        )
        vector_index = langchain_postgres.v2.indexes.HNSWIndex()
        if metadata_columns_names:
            create_index(
                engine=engine,
                table_name=table_name,
                columns=metadata_columns_names,
                unique=ensure_metadata_columns_index_is_unique,
            )

    store = langchain_postgres.PGVectorStore.create_sync(
        engine=pg_engine,
        table_name=table_name,
        embedding_service=embeddings,
        metadata_columns=metadata_columns_names,
        k=retrieved_document_count,
        fetch_k=5 * retrieved_document_count,
    )
    if vector_index:
        store.apply_vector_index(vector_index)
    else:
        store.reindex()

    return store

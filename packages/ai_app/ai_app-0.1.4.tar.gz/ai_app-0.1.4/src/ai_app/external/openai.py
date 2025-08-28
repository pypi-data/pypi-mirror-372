import os
import urllib
from typing import Iterable

import langchain_core.messages
import openai
import polars as pl
import pydantic
import requests

from ai_app.utils import unnest_with_prefix


def get_openai_api_url():
    return "https://api.openai.com"


def prepare_request(
    messages: Iterable[langchain_core.messages.BaseMessage],
    model: str = "gpt-4o-mini",
    structured_output: pydantic.BaseModel | None = None,
    strict_output: bool = False,
    method: str = "POST",
    path: str = "v1/chat/completions",
    api_key: str | None = None,
) -> requests.Request:
    """
    The structured_output is expected to have a config dict compatible with OpenAI structured output schema format.
    Returns a well-formed HTTP request that, for example, can be used with the `requests` library:
        `response = requests.request(**vars(request))`
    """
    url = urllib.parse.urljoin(get_openai_api_url(), path)
    messages = langchain_core.messages.convert_to_openai_messages(messages)
    data = {
        "messages": messages,
        "model": model,
    }
    if structured_output:
        data["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "schema": structured_output.model_json_schema(mode="serialization"),
                "name": structured_output.__name__,
                "strict": strict_output,
            },
        }

    headers = {
        "Content-Type": "application/json",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    request = requests.Request(method=method, url=url, headers=headers, json=data)
    return request


def write_openai_batch_api_jsonl(requests_: list[requests.Request], path: str) -> None:
    if os.path.exists(path):
        os.remove(path)

    # Requests are written one by one to prevent polars from coalescting struct columns by adding
    # None values to missing fields.
    with open(path, "a") as f:
        for index, request in enumerate(requests_):
            df = pl.DataFrame([vars(request)])
            df = df.select(
                pl.lit(str(index)).alias("custom_id"),
                pl.col("url").str.strip_prefix(get_openai_api_url()),
                "method",
                pl.col("json").alias("body"),
            )
            df.write_ndjson(f)


def create_openai_batch(
    path: str,
    client: openai.OpenAI | None = None,
    endpoint: str = "/v1/chat/completions",
    metadata: dict | None = None,
    rename_file: bool = False,
):
    client = client or openai.OpenAI()
    with open(path, "rb") as f:
        input_file = client.files.create(file=f, purpose="batch")

    if rename_file:
        directory, file = os.path.split(path)
        new_path = os.path.join(directory, input_file.id)
        os.rename(path, new_path)

    batch = client.batches.create(
        input_file_id=input_file.id,
        endpoint=endpoint,
        completion_window="24h",
        metadata=metadata,
    )
    return batch


def openai_collection_to_dataframe(
    collection: Iterable[pydantic.BaseModel], time_zone: str = "Asia/Baku"
) -> pl.DataFrame | None:
    df = pl.DataFrame([i.model_dump() for i in collection], infer_schema_length=None)
    if df.is_empty():
        return

    epoch_columns = [c for c in df.columns if c.endswith("_at") and df.schema[c].is_integer()]
    df = df.with_columns(pl.from_epoch(c).dt.convert_time_zone(time_zone) for c in epoch_columns)
    return df


def fetch_openai_files_metadata(
    client: openai.OpenAI | None = None, limit: int = 10_000, **kwargs
) -> pl.DataFrame | None:
    client = client or openai.OpenAI()
    files = client.files.list(limit=limit, **kwargs)
    df = openai_collection_to_dataframe(files)
    return df


def fetch_openai_batches_metadata(
    client: openai.OpenAI | None = None, limit: int = 100, **kwargs
) -> pl.DataFrame:
    client = client or openai.OpenAI()
    batches = client.batches.list(limit=limit, **kwargs)
    df = openai_collection_to_dataframe(batches)
    df = unnest_with_prefix(df, "request_counts")
    files = fetch_openai_files_metadata()
    if files is not None:
        files = files.select(
            pl.col("filename").alias("input_filename"),
            pl.col("id").alias("input_file_id"),
        )
        df = df.join(files, on="input_file_id", how="left")

    return df


def try_fetch_batch_output(
    batch_id: str, client: openai.OpenAI | None = None
) -> pl.DataFrame | None:
    client = client or openai.OpenAI()
    batch = client.batches.retrieve(batch_id)
    if not batch.output_file_id:
        return

    file = client.files.content(batch.output_file_id)
    df = pl.read_ndjson(file.content)
    df = df.unnest("response")
    df = unnest_with_prefix(df, "body")
    if (df["body_choices"].list.len() == 1).all():
        df = df.with_columns(pl.col("body_choices").list[0].struct["message"].struct["content"])

    return df

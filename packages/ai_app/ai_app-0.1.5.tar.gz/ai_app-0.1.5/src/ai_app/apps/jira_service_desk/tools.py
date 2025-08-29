import functools
import inspect
import json
from typing import Annotated, override

import langchain.tools
import langchain_postgres
import logfire
import pydantic

from ai_app.ai_utils import json_dumps_for_ai
from ai_app.apps.jira_service_desk.data import (
    JiraRequest,
    JiraRequestCommonColumns,
    JiraRequestPrimaryKey,
    JiraRequestType,
    fetch_guides,
    fetch_use_case_guides_for_requests,
    get_index_column_names,
)
from ai_app.config import get_ai_postgres_rag_engine, get_config
from ai_app.rag import build_postgres_vector_store
from ai_app.tools.base import BaseToolkit


def build_postgres_jira_request_use_cases_ai_summary_vector_store(
    **kwargs,
) -> langchain_postgres.PGVectorStore:
    metadata_columns = [
        langchain_postgres.Column(c, data_type="int") for c in get_index_column_names()
    ]
    store = build_postgres_vector_store(
        engine=get_ai_postgres_rag_engine(),
        openai_api_key=get_config().secrets.openai_api_key,
        table_name="jira_request_use_cases_ai_summary",
        metadata_columns=metadata_columns,
        ensure_metadata_columns_index_is_unique=True,
        **kwargs,
    )
    return store


@functools.cache
def get_postgres_vector_store() -> langchain_postgres.PGVectorStore:
    return build_postgres_jira_request_use_cases_ai_summary_vector_store()


class JiraServiceDeskToolkit(BaseToolkit):
    def __init__(self, n_closest_requests: int = 5, service_desks: list[int] | None = None):
        super().__init__()
        self.n_closest_requests = n_closest_requests
        self.service_desks = service_desks

    @override
    def get_tools(self) -> list[langchain.tools.BaseTool]:
        tools = [
            self.fetch_jira_request_type_guides_closest_to_user_query,
            fetch_detailed_jira_request_type_guide,
            build_url_for_jira_request_type,
        ]
        tools = [langchain.tools.tool(t) for t in tools]
        return tools

    @logfire.instrument()
    async def fetch_jira_request_type_guides_closest_to_user_query(
        self, query_in_english: str
    ) -> str:
        """Fetches Jira request type guides with use cases closest to user query via RAG."""
        store = get_postgres_vector_store()
        metadata_filter = (
            dict(service_desk_id={"$in": self.service_desks}) if self.service_desks else None
        )
        with logfire.span("Postgres vector store similarity search"):
            documents = await store.asimilarity_search(
                query_in_english, k=self.n_closest_requests, filter=metadata_filter
            )

        primary_keys = [JiraRequestPrimaryKey(**d.metadata) for d in documents]
        guides = fetch_use_case_guides_for_requests(primary_keys)
        guides = json_dumps_for_ai(guides)
        return guides


def fetch_detailed_jira_request_type_guide(service_desk_id: int, request_type_id: int) -> str:
    """
    Fetches Jira request type guide with information about when to use it and how the requests of
    this type are usually resolved. Additionally may return manually specified details which
    are more important than others, and in case of contradictions, the manually specified
    details take precedence.
    """
    primary_keys = [
        JiraRequestPrimaryKey(service_desk_id=service_desk_id, request_type_id=request_type_id)
    ]
    guides: list[JiraRequestType] = fetch_guides(primary_keys, with_input_fields=True)
    if len(guides) != 1:
        raise RuntimeError(f"Expected to fetch 1 guide, but got {len(guides)}")

    guide = guides[0]
    ai_input_fields = {field.field_id: field.description for field in guide.ai.input_request_fields}
    input_fields = [
        field.model_dump(exclude=list(JiraRequestCommonColumns.model_fields))
        | {"ai_generated_description": ai_input_fields.get(field.field_id)}
        for field in guide.meta.input_request_fields
    ]
    guide = dict(
        service_desk_id=guide.meta.service_desk_id,
        request_type_id=guide.meta.request_type_id,
        request_type_name=guide.meta.name,
        request_url=guide.meta.build_url(),
        use_case_summary=guide.ai.use_case,
        manually_specified_use_case_overrides=guide.manual.use_case,
        resolution_pipeline=guide.ai.resolution_pipeline,
        self_help=guide.ai.self_help,
        manually_specified_resolution_overrides=guide.manual.resolution,
        input_fields=input_fields,
    )
    guide = json_dumps_for_ai(guide)
    return guide


def build_url_for_jira_request_type(
    service_desk_id: int,
    request_type_id: int,
    request_type_name: str,
    # OpenAI models struggled to generate tool calls for `dict[str, str]` or `**kwargs: str`
    # arguments, so I switched to a more straightforward single JSON string argument instead.
    input_request_fields_json: Annotated[
        str,
        pydantic.Field(
            description=inspect.cleandoc(
                """
                The JSON with string key-value pairs for the Jira request input fields.
                The keys are the internal input_fields' field_ids taken from the output of the
                fetch_detailed_jira_request_type_guide tool, for which the
                can_be_passed_as_url_parameter is true.
                The values should align with the input field description and valid_values list,
                if present.
                """
            ),
        ),
    ],
) -> str:
    """
    Build a markdown URL for a Jira request type.
    The input field values should be provided in the input_request_fields_json argument.
    The URL will redirect to the Jira request creation page with prefilled values for these fields.
    """
    jira_request = JiraRequest(
        service_desk_id=service_desk_id,
        request_type_id=request_type_id,
        name=request_type_name,
    )
    input_request_fields = json.loads(input_request_fields_json)
    url = jira_request.build_markdown_url(**input_request_fields)
    return url

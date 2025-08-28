import datetime
import json
import logging
import textwrap
import warnings

import atlassian
import langchain_core.documents
import polars as pl
import pydantic
import requests
import sqlmodel
import tqdm.auto

from ai_app.ai_utils import (
    SummarizationStateBase,
    Summarizer,
    get_pydantic_config_dict_for_openai_structured_output,
    process_nested_basic_datatypes,
    to_json_llm_input,
    try_converting_to_openai_flex_tier,
)
from ai_app.apps.jira_service_desk.data import (
    AiInputRequestFields,
    AiJiraRequestGuide,
    AiJiraRequestGuideContent,
    InputRequestField,
    JiraRequest,
    JiraRequestCommonColumns,
    ManualJiraRequestGuide,
    build_row_index,
    get_index_column_names,
    get_saved_request_type_primary_keys,
)
from ai_app.apps.jira_service_desk.tools import get_postgres_vector_store
from ai_app.config import (
    get_ai_postgres_engine,
    get_anon_codec,
    get_chat_model,
    get_jira,
    get_service_desk,
)
from ai_app.external.atlassian import (
    build_request_url,
    extract_issue_field_values,
    generate_jql_issues,
    get_jira_base_url,
    get_request_field_names,
    get_request_fields,
    get_service_desks,
    get_service_desks_request_types,
    normalize_line_breaks,
)
from ai_app.external.google import Spreadsheets
from ai_app.sql import open_session


def get_request_common_field_names() -> dict[str, str]:
    fields = {
        "resolution": "Resolution",
        "reporter": "Reporter",
        "assignee": "Assignee",
    }
    return fields


def get_irrelevant_request_fields() -> dict[str, str]:
    fields = {
        "attachment": "Attachment",
        "customfield_10300": "Approvers",
        "approvers": "Approvers",
    }
    return fields


def get_request_resolution_statuses() -> set[str]:
    statuses = {
        "Done",
        "Rejected",
        "Resolved",
        "No response",
        "Won't Do",
        "Declined",
        "Unresolved",
        "Duplicate",
    }
    return statuses


# def get_service_desk_ids_to_ignore() -> set[int]:
#     ids = {
#         23,  # Pasha Bank Georgia.
#         42,  # Pasha service desk, which I don't have access to.
#         442,  # No access, Jira project TB.
#     }
#     return ids


def update_jira_requests():
    """
    Updates {JiraRequest} and {InputRequestField} tables by collecting all the request types
    for all service desks from Jira API. Delete service desks and request types that are no longer
    present in Jira or that the API key doesn't have access to.
    """
    engine = get_ai_postgres_engine()
    jira = get_jira()
    service_desk = get_service_desk()
    service_desks = set()
    for service_desk_id, desk in get_service_desks(service_desk).items():
        try:
            jira.get_project(desk["projectKey"])
        except requests.HTTPError:
            logging.warning(
                f"No access to Jira project {desk['projectKey']}, skipping service desk."
            )
        else:
            service_desks.add(service_desk_id)

    with open_session(engine, commit_on_exit=True) as session:
        session.exec(
            sqlmodel.delete(JiraRequest).where(JiraRequest.service_desk_id.notin_(service_desks))
        )

    for service_desk_id in service_desks:
        service_desks_request_types = get_service_desks_request_types(
            service_desk=service_desk,
            service_desk_id=service_desk_id,
            verbose=True,
        )
        with open_session(engine, commit_on_exit=True) as session:
            session.exec(
                sqlmodel.delete(JiraRequest).where(
                    JiraRequest.service_desk_id == service_desk_id,
                    JiraRequest.request_type_id.notin_(service_desks_request_types),
                )
            )
            for request_type_id, request_type in tqdm.auto.tqdm(
                service_desks_request_types.items()
            ):
                index = build_row_index(
                    service_desk_id=service_desk_id,
                    request_type_id=request_type_id,
                )
                request = JiraRequest(
                    **index,
                    name=request_type["name"],
                    description=request_type.get("description"),
                )
                session.merge(request)

                try:
                    request_fields_df = get_request_fields(
                        service_desk=service_desk,
                        service_desk_id=service_desk_id,
                        request_type_id=request_type_id,
                    )
                except Exception:
                    warnings.warn(
                        f"Failed to get request fields for service desk {service_desk_id} "
                        f"and request type {request_type_id}\n"
                        f"Request URL: {build_request_url(service_desk_id, request_type_id)}"
                    )
                    raise

                if request_fields_df is not None:
                    for row in request_fields_df.iter_rows(named=True):
                        field = InputRequestField(
                            **index,
                            field_id=row["fieldId"],
                            name=row["name"],
                            description=row["description"],
                            can_be_passed_as_url_parameter=row["can_be_passed_as_url_parameter"],
                            valid_values=row["valid_value_labels"],
                        )
                        session.merge(field)


def update_manual_jira_requests(
    spreadsheets: Spreadsheets,
    sheet_name: str = "Service desk requests",
    write_back_to_gsheet: bool = False,
):
    f"""Updates {ManualJiraRequestGuide} table."""

    index_columns = get_index_column_names()
    df = spreadsheets.read_sheet(sheet_name)
    df = df.select(
        *(pl.col(c).str.to_integer() for c in index_columns + ["do_recommend"]),
        "use_case",
        "resolution",
    )
    saved_request_primary_keys = get_saved_request_type_primary_keys(get_ai_postgres_engine())
    saved_request_primary_keys = {i.primary_key_tuple for i in saved_request_primary_keys}
    with open_session(get_ai_postgres_engine()) as session:
        for row in df.iter_rows(named=True):
            guide = ManualJiraRequestGuide(**row)
            if guide.primary_key_tuple not in saved_request_primary_keys:
                warnings.warn(
                    f"Request type primary key from manual description not found among saved: "
                    f"{guide.primary_key_tuple}"
                )
            else:
                session.merge(guide)

        session.commit()

    if write_back_to_gsheet:
        ai_df = pl.read_database(sqlmodel.select(AiJiraRequestGuide), get_ai_postgres_engine())
        columns_to_drop = set(JiraRequestCommonColumns.model_fields) - set(index_columns)
        ai_df = ai_df.drop(columns_to_drop)
        ai_df = ai_df.rename({c: f"ai_{c}" for c in set(ai_df.columns) - set(index_columns)})

        jira_df = pl.read_database(sqlmodel.select(JiraRequest), get_ai_postgres_engine())
        jira_df = jira_df.drop(columns_to_drop)
        base_url = get_jira_base_url()
        url = f"{base_url}/servicedesk/customer/portal/{{}}/create/{{}}"
        jira_df = jira_df.with_columns(pl.format(url, *index_columns).alias("url"))
        jira_df = jira_df.rename(
            {c: f"jira_{c}" for c in set(jira_df.columns) - set(index_columns)}
        )

        jira_df = jira_df.join(ai_df, on=index_columns, how="left")
        df = jira_df.join(df, on=index_columns, how="left")
        df = df.with_columns(pl.col("do_recommend").fill_null(0))
        spreadsheets.write_sheet(sheet_name, df)


def build_structured_output_class(
    input_attributes: list[str],
    parent_class: type[pydantic.BaseModel] = AiJiraRequestGuideContent,
) -> type:
    InputRequestFields = pydantic.create_model(
        "InputRequestFields",
        __config__=get_pydantic_config_dict_for_openai_structured_output(),
        __doc__=textwrap.dedent(
            """
            A collection of request attributes that the user needs to provide,
            with short description, common user errors (if present) and example for each
            """
        ),
        **{i: (str, ...) for i in input_attributes},
    )

    class JiraRequestUserGuide(
        parent_class, **get_pydantic_config_dict_for_openai_structured_output()
    ):
        input_request_fields: InputRequestFields

    return JiraRequestUserGuide


def fetch_issue_comments(service_desk: atlassian.ServiceDesk, issue: dict, limit_comments: int):
    issue_comments = service_desk.get_request_comments(issue["Issue key"], limit=limit_comments)
    issue_comments = sorted(issue_comments, key=lambda c: c["created"]["iso8601"])
    issue_comments = [(c["author"]["displayName"], c["body"]) for c in issue_comments]
    participants = {
        issue["Reporter"]: "Reporter",
        issue["Assignee"]: "Assignee",
    }
    issue_comments = [
        (participants.get(author, author), normalize_line_breaks(body))
        for author, body in issue_comments
    ]
    issue_comments = [f"{author}: {body}" for author, body in issue_comments]
    return issue_comments


def generate_requests(
    service_desk_id: int,
    request_type_id: int,
    jql_filter: str | None = None,
    fields: dict[str, str] | None = None,
    lookbehind: datetime.timedelta = datetime.timedelta(days=365),
    limit_requests: int = 100,
    limit_comments: int = 50,
    verbose: bool = False,
):
    jira = get_jira()
    service_desk = get_service_desk()
    fields = dict(fields or get_request_field_names(service_desk, service_desk_id, request_type_id))
    fields |= get_request_common_field_names()
    fields = {k: v for k, v in fields.items() if k not in get_irrelevant_request_fields()}
    service_desk_name_project = get_service_desks(service_desk)[service_desk_id]["projectKey"]
    request_type_name = get_service_desks_request_types(service_desk, service_desk_id)[
        request_type_id
    ]["name"]
    request_type_name = request_type_name.replace("\t", r"\t")
    jql_filter = jql_filter or textwrap.dedent(f"""
        resolution IS NOT EMPTY
        AND resolution NOT IN ('No response')
        AND resolutiondate > {datetime.date.today() - lookbehind}
    """)
    jql = f"""
        project = {service_desk_name_project}
        AND 'customer request type' = '{request_type_name} ({service_desk_name_project})'
        AND ({jql_filter})
        ORDER BY resolutiondate DESC
    """  # noqa: E501
    for issue in generate_jql_issues(
        jira=jira, jql=jql, fields=list(fields), soft_limit=limit_requests, verbose=verbose
    ):
        issue = extract_issue_field_values(issue)
        issue = {fields.get(k, k): v for k, v in issue.items()}
        issue["Comments"] = fetch_issue_comments(service_desk, issue, limit_comments)
        yield issue


def get_request(issue_key: str) -> dict:
    jira = get_jira()
    issue = jira.get_issue(issue_key)
    return issue


def update_ai_jira_request_guides(service_desk_ids: list[int] | None = None, **kwargs):
    f"""Updates {AiJiraRequestGuide} table."""
    # TODO: convert to async, use asyncio.TaskGroup for concurrent execution.
    statement = sqlmodel.select(JiraRequest)
    if service_desk_ids:
        statement = statement.where(JiraRequest.service_desk_id.in_(service_desk_ids))

    with open_session(get_ai_postgres_engine()) as session:
        for request in tqdm.auto.tqdm(
            session.exec(statement),
            desc="Iterating over Jira request types from the JiraRequest table",
        ):
            summarize_request_type(request.service_desk_id, request.request_type_id, **kwargs)


class SummarizationState(AiJiraRequestGuideContent, SummarizationStateBase): ...


def summarize_request_type(
    service_desk_id: int, request_type_id: int, model=None, max_tokens: int = 800_000, **kwargs
) -> AiJiraRequestGuide | None:
    index = build_row_index(service_desk_id=service_desk_id, request_type_id=request_type_id)
    output_attributes = ["Resolution", "Comments"]
    meta_attributes = ["Issue key", "Reporter", "Assignee", "Approvers"]
    fields = get_request_field_names(get_service_desk(), service_desk_id, request_type_id)
    input_attributes = list(set(fields.values()) - set(output_attributes) - set(meta_attributes))
    SummarizationStateWithFields = build_structured_output_class(
        input_attributes=input_attributes,
        parent_class=SummarizationState,
    )
    if not model:
        model = get_chat_model("gpt-5-mini")
        model = try_converting_to_openai_flex_tier(model)
        # See docs for more OpenAI API parameters:
        # https://platform.openai.com/docs/api-reference/responses/create#responses_create-reasoning
        model = model.model_copy(
            update={
                "reasoning": {
                    "effort": "medium",
                    # "summary": "detailed", # Requires the OpenAI organization to be verified.
                },
            }
        )

    summarizer = Summarizer(
        model=model,
        max_tokens=max_tokens,
        context=build_summarization_context_prompt(**index, input_attributes=input_attributes),
    )
    items = generate_requests(**index, fields=fields, verbose=True, **kwargs)
    anon_codec = get_anon_codec()
    items = process_nested_basic_datatypes(items, process_string=anon_codec.anonymize)
    items = [json.dumps(i, ensure_ascii=False) for i in items]
    state = summarizer.summarize(state=SummarizationStateWithFields, items=items)
    if not state:
        return

    ai_request_guide = AiJiraRequestGuide(
        **index,
        **state.model_dump(include=list(AiJiraRequestGuideContent.model_fields)),
    )
    with open_session(get_ai_postgres_engine()) as session:
        session.merge(ai_request_guide)
        for field_name, description in state.input_request_fields.model_dump().items():
            field = AiInputRequestFields(
                **index,
                field_id=fields.inverse[field_name],
                description=description,
            )
            session.merge(field)

        session.commit()

    update_ai_jira_request_guide_embedding(ai_request_guide)
    return ai_request_guide


def build_summarization_context_prompt(
    service_desk_id: int, request_type_id: int, input_attributes: list[str]
) -> str:
    service_desk_name = get_service_desks(get_service_desk())[service_desk_id]["projectName"]
    request_type_name = get_service_desks_request_types(get_service_desk(), service_desk_id)[
        request_type_id
    ]["name"]
    context = {
        "Organization": (
            "Kapital Bank, a bank in Azerbaijan servicing both retail and corporate customers, "
            "providing services both at physical branches and digitally online."
        ),
        "Jira Service Desk name": service_desk_name,
        "Request type": request_type_name,
        "Request attributes that were provided by users": input_attributes,
    }
    prompt = textwrap.dedent("""
        I work at an organization where we use a Jira service desk to manage various requests. 
        Help me analyze resolved requests of one specific type from this service desk to create a guide for new users. 
        This guide should explain when to use this request type (the situations or problems it solves) 
        and how to correctly fill in information for this request type.

        You will be provided with a **JSON** list containing multiple **resolved requests** of the same request type.
        Each item in the list corresponds to an individual request with same attributes for all requests.
        All attribute values were **provided by users** when creating the requests, except for the following attributes:
        - **Resolution**: Indicates the outcome of the request, where "Done" and "Resolved" signifies a successful resolution, 
            while "Rejected", "Won't Do", "Declined" and "Unresolved" usually means the request was incorrectly formulated or not approved.
        - **Comments**: Contains the **discussion history** and any communication between the request participants during the resolution process. 
            The format is a list of strings with comment author in the prefix, for example:
            ```json
            [
                "Reporter: Please help me change the password",
                "Assignee: Hello, the link was sent in email",
                "Reporter: Thank you",
            ]
            ```

        ### Your Task
        1. **Analyze the provided requests** to determine:
        - **What kind of problems this request type solves** (e.g., customer issues, operational tasks, or system-related inquiries).
        - **What information a user needs to provide** to ensure the request is accurately processed and resolved. 
            For each attribute field that the user needs to provide, generate a short description and explain why this attribute is needed 
            and how it affects request resolution.
        - **How the request is resolved** - the steps typically taken by both the **reporter** and **assignee** to resolve these requests.

        2. **Language consideration**:
        - Be aware that most of the data will be in **Azerbaijani**. Interpret the content accordingly while identifying patterns and extracting 
            relevant information. But note that the output should be in **English**.

        ### Additional Context
        Additional information regarding the environment in which the requests were created, meant to clarify references used in requests 
        and aid in creating an informed user guide:
    """) + to_json_llm_input(context)  # noqa: E501
    return prompt


def update_ai_jira_request_guide_embedding(guide: AiJiraRequestGuide):
    metadata = guide.model_dump(include=get_index_column_names())
    document = langchain_core.documents.Document(
        page_content=guide.use_case,
        metadata=metadata,
    )
    store = get_postgres_vector_store()
    existing_documents_with_same_metadata = store.similarity_search_by_vector(
        [0] * store.embeddings.dimensions, k=1000, filter=metadata
    )
    store.delete([d.id for d in existing_documents_with_same_metadata])
    store.add_documents([document])


def update_all_ai_jira_request_guide_embeddings():
    with open_session(get_ai_postgres_engine()) as session:
        statement = sqlmodel.select(AiJiraRequestGuide)
        for guide in tqdm.auto.tqdm(session.exec(statement), desc="Updating embeddings"):
            update_ai_jira_request_guide_embedding(guide)

import datetime
import textwrap

import pydantic
import sqlalchemy as sa
import sqlmodel

from ai_app.config import get_ai_postgres_engine
from ai_app.external.atlassian import build_request_url
from ai_app.sql import build_foreign_key_constraint, open_session
from ai_app.utils import get_utc_now


class JiraRequestPrimaryKey(sqlmodel.SQLModel):
    service_desk_id: int = sqlmodel.Field(
        primary_key=True,
        alias="Service desk id",
    )
    request_type_id: int = sqlmodel.Field(
        primary_key=True,
        alias="Request type id",
    )

    @property
    def primary_key_tuple(self) -> tuple[int, int]:
        key = self.service_desk_id, self.request_type_id
        return key

    def __hash__(self) -> int:
        return hash(self.primary_key_tuple)

    @classmethod
    def get_sa_primary_key(cls):
        key = sa.tuple_(
            cls.service_desk_id,
            cls.request_type_id,
        )
        return key

    def build_url(self, **parameters) -> str:
        url = build_request_url(
            service_desk_id=self.service_desk_id,
            request_type_id=self.request_type_id,
            **parameters,
        )
        return url


class JiraRequestCommonColumns(JiraRequestPrimaryKey):
    updated_at: datetime.datetime | None = sqlmodel.Field(
        default_factory=get_utc_now,
        sa_column_kwargs={"onupdate": get_utc_now},
    )


def get_index_column_names() -> list[str]:
    columns = ["service_desk_id", "request_type_id"]
    assert all(c in JiraRequestCommonColumns.model_fields for c in columns)
    return columns


def build_row_index(service_desk_id: int, request_type_id: int) -> dict:
    index = dict(service_desk_id=service_desk_id, request_type_id=request_type_id)
    return index


# Note that table=True disables Pydantic validation at instantiation.
class JiraRequest(JiraRequestCommonColumns, table=True):
    """
    Contains Jira request metadata extracted from Jira API.

    Input fields for the request type:
    If present, the field named "Approvers" should contain the names of employees that need to
    approve the request, which are usually the user's superiors or owners of some systems related to
    the request.
    If present, the "Attachment" field allows for uploading files together with the request,
    such as screenshots or text documents.
    """

    name: str = sqlmodel.Field(description="Jira request type name")
    description: str | None = sqlmodel.Field(
        default=None, description="Jira request type description"
    )
    input_request_fields: list["InputRequestField"] = sqlmodel.Relationship()

    def build_markdown_url(self, **parameters) -> str:
        url = self.build_url(**parameters)
        url = f"[{self.name}]({url})"
        return url


class InputRequestField(JiraRequestCommonColumns, table=True):
    """A request field that needs to be provided by the user when creating a Jira request."""

    __table_args__ = (build_foreign_key_constraint(JiraRequest),)

    field_id: str = sqlmodel.Field(primary_key=True)
    name: str
    valid_values: list[str] | None = sqlmodel.Field(
        default=None,
        description="If not null, then the value for this field must be from this list, otherwise it can be any string.",
        nullable=True,
        sa_type=sa.ARRAY(sa.String),
    )
    can_be_passed_as_url_parameter: bool
    description: str | None = None


class AiJiraRequestGuideContent(sqlmodel.SQLModel):
    """
    A guide to help new users understand the appropriate use of the specific Jira request type
    through clear examples and generalized scenarios, avoiding direct quotes from resolved issues
    to protect privacy and enhance learning.
    """

    use_case: str = sqlmodel.Field(
        description=textwrap.dedent("""
            Comprehensive description of when to use this request type and what problems it solves.
            Include common user queries and problem statements to help with RAG-based matching
            in support chats. Focus on real-world scenarios and typical user needs.
        """)
    )
    resolution_pipeline: str = sqlmodel.Field(
        description=(
            "The usual process that takes place in order to resolve the issue, "
            "along with an example."
        )
    )
    self_help: str | None = sqlmodel.Field(
        default=None,
        description="The ways in which the user can try resolving the issue themselves, if any.",
    )


class AiJiraRequestGuide(AiJiraRequestGuideContent, JiraRequestCommonColumns, table=True):
    """Contains AI generated summary and resolution guide for a Jira request type."""

    __table_args__ = (build_foreign_key_constraint(JiraRequest),)

    input_request_fields: list["AiInputRequestFields"] = sqlmodel.Relationship()


class AiInputRequestFields(JiraRequestCommonColumns, table=True):
    __table_args__ = (build_foreign_key_constraint(AiJiraRequestGuide),)

    field_id: str = sqlmodel.Field(primary_key=True)
    description: str | None = None


class ManualJiraRequestGuide(JiraRequestCommonColumns, table=True):
    """
    Contains manual summary, problem description and additional handling instructions for a Jira
    request type.
    """

    __table_args__ = (build_foreign_key_constraint(JiraRequest),)

    do_recommend: bool = sqlmodel.Field(
        default=True,
        alias="Do recommend",
        description="Whether this request type should be recommended to users.",
    )
    use_case: str | None = sqlmodel.Field(
        default=None,
        alias="Use case",
        description="Use case for this request type, mainly used to modify AI generated use case.",
    )
    resolution: str | None = sqlmodel.Field(
        default=None,
        alias="Resolution",
        description=(
            "The usual process that takes place in order to resolve the issue, "
            "mainly used to modify AI generated resolution and self help."
        ),
    )


def get_saved_request_type_primary_keys(
    engine: sa.Engine, *where_clauses
) -> set[JiraRequestPrimaryKey]:
    statement = sqlmodel.select(JiraRequest.service_desk_id, JiraRequest.request_type_id)
    statement = statement.where(*where_clauses)
    with open_session(engine) as session:
        result = session.exec(statement)
        primary_keys = {JiraRequestPrimaryKey(**pk) for pk in result.mappings()}

    return primary_keys


class JiraRequestType(pydantic.BaseModel):
    meta: JiraRequest
    ai: AiJiraRequestGuide
    manual: ManualJiraRequestGuide


def fetch_guides(
    primary_keys: list[JiraRequestPrimaryKey] | None = None,
    only_recommended: bool = False,
    with_input_fields: bool = False,
    engine: sa.Engine | None = None,
) -> list[JiraRequestType]:
    statement = sqlmodel.select(JiraRequest, AiJiraRequestGuide, ManualJiraRequestGuide).where(
        AiJiraRequestGuide.get_sa_primary_key().in_([pk.primary_key_tuple for pk in primary_keys])
        if primary_keys is not None
        else sa.true(),
        AiJiraRequestGuide.get_sa_primary_key() == ManualJiraRequestGuide.get_sa_primary_key(),
        AiJiraRequestGuide.get_sa_primary_key() == JiraRequest.get_sa_primary_key(),
        ManualJiraRequestGuide.do_recommend if only_recommended else sa.true(),
    )
    if with_input_fields:
        statement = statement.options(
            sa.orm.selectinload(JiraRequest.input_request_fields),
            sa.orm.selectinload(AiJiraRequestGuide.input_request_fields),
        )

    with open_session(engine or get_ai_postgres_engine()) as session:
        guides = list(session.exec(statement))

    guides = [JiraRequestType(meta=meta, ai=ai, manual=manual) for meta, ai, manual in guides]
    return guides


def fetch_use_case_guides_for_requests(primary_keys: list[JiraRequestPrimaryKey]) -> list[dict]:
    guides: list[JiraRequestType] = fetch_guides(primary_keys, only_recommended=True)
    guides = [
        dict(
            service_desk_id=guide.meta.service_desk_id,
            request_type_id=guide.meta.request_type_id,
            request_url=guide.meta.build_markdown_url(),
            request_type_name=guide.meta.name,
            do_recommend_to_user=guide.manual.do_recommend,
            use_case_summary=guide.ai.use_case,
            manually_specified_use_case_overrides=guide.manual.use_case,
        )
        for guide in guides
    ]
    return guides

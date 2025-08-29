import collections
import logging
from typing import Any

import langchain.tools
import langchain_core.messages
import langchain_core.tools
import pydantic

from ai_app.tools.atlassian import ConfluenceToolkit, JiraToolkit
from ai_app.tools.gitlab import GitLabToolkit
from ai_app.tools.meta import (
    InfoSecUserReminder,
    MetaToolkit,
    report_disclosure_of_sensitive_information,
    report_feedback,
    report_masked_entities_difficulties,
)
from ai_app.tools.sonarqube import SonarQubeToolkit
from ai_app.tools.sql import SqlToolkit


def extract_tool_artifacts_from_agent_response(
    messages: list[langchain_core.messages.BaseMessage],
) -> dict[str, list]:
    artifacts = collections.defaultdict(list)
    for message in messages:
        if isinstance(message, langchain_core.messages.ToolMessage) and message.artifact:
            artifacts[message.name].append(message.artifact)

    artifacts = dict(artifacts)
    return artifacts


def build_structured_response_tool(Response: type[pydantic.BaseModel]):
    """
    Structured output tool can decrease the number of model calls, but may be less reliable.
    It has additional benefit that the model sees the structured response schema in the ReAct loop,
    while the builtin implementation provides it to the agent after exiting the ReAct loop.
    Note that the docstring of the Response class is NOT passed to the model,
    only fields descriptions are.
    https://langchain-ai.github.io/langgraph/how-tos/react-agent-structured-output/#option-1-bind-output-as-tool
    """

    @langchain.tools.tool(
        args_schema=Response, return_direct=True, response_format="content_and_artifact"
    )
    def return_response(**kwargs) -> tuple[str, Response]:
        """Return response and end agent loop."""
        content = "Response was processed successfully."
        artifact = Response(**kwargs)
        return content, artifact

    return return_response


def get_structured_output_from_agent_response(response: dict) -> pydantic.BaseModel | None:
    if structured_response := response.get("structured_response"):
        return structured_response

    artifacts = extract_tool_artifacts_from_agent_response(response["messages"])
    artifacts = artifacts.get(build_structured_response_tool(None).name)
    # Take last structured response artifact.
    structured_response = artifacts[-1] if artifacts else None
    return structured_response


def think(thouhts: str) -> None:
    """This tool can be used to reason about the next steps and to create a plan."""
    # Note that since models generate tool calls independently and in parallel, this tool
    # call doesn't affect other calls. So if the thinking is required (for non-reasoning models)
    # before calling tools, then either the tools themselves should have "thoughts" as first
    # argument, or a separate reasoning API call should be made beforehand.

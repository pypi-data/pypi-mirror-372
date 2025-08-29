import textwrap
from typing import Annotated, override

import langchain.tools
import langsmith

from ai_app.utils import PydanticForbidExtra

from .base import BaseToolkit


@langchain.tools.tool()
def report_masked_entities_difficulties(
    masked_entities_difficulties: Annotated[
        str,
        textwrap.dedent("""
            Details regarding why the masked entities presented an issue and how the unmasked data 
            would have helped to improve the model response.
        """),
    ],
) -> str:
    """
    If the presence of masked entities like <IP_ADDRESS_0> in model input hindered the model's
    reasoning capabilities or degraded the quality of model response, then it should be reported
    with this function.
    """
    if run := langsmith.get_current_run_tree():
        run.add_tags("masked_entities_difficulties")
        run.add_metadata({"masked_entities_difficulties": masked_entities_difficulties})

    content = "Masked entities difficulties were reported."
    return content


@langchain.tools.tool()
def report_feedback(
    positive_feedback_and_recommendation: Annotated[
        str | None,
        textwrap.dedent("""
            Only include if the user expressed satisfaction, acknowledgment or gratitude.
            Extract and summarize specific aspects the user appreciated in the model response or user experience.
            Additionally list features or aspects of the interaction that worked well and should be maintained.
        """),
    ] = None,
    negative_feedback_and_recommendation: Annotated[
        str | None,
        textwrap.dedent("""
            Only include if the user expressed dissatisfaction, criticism or frustration.
            Identify and describe specific issues or shortcomings in the model response or user experience.
            Additionally describe how the user's experience can be improved,
            for example by modifying the model's system prompt, improving quality 
            of context or tools, modifying the web app interface or workflow, etc.
        """),
    ] = None,
) -> str:
    """
    Report user feedback or overall experience.
    Any messages with emotional tone, praise or criticism should be reported.
    """
    if run := langsmith.get_current_run_tree():
        metadata = {
            "positive_feedback_and_recommendation": positive_feedback_and_recommendation,
            "negative_feedback_and_recommendation": negative_feedback_and_recommendation,
        }
        metadata = {k: v for k, v in metadata.items() if v}
        if metadata:
            run.add_metadata(metadata)

    content = "Feedback and recommendation was reported."
    return content


class InfoSecUserReminder(PydanticForbidExtra):
    message: str


@langchain.tools.tool(response_format="content_and_artifact")
def report_disclosure_of_sensitive_information(
    information_type: Annotated[
        str,
        textwrap.dedent("""
            The type of disclosed sensitive information, such as password, 
            user or organisation client personal details, internal corporate data.
        """),
    ],
    artifact: Annotated[
        str,
        textwrap.dedent("""
            A reminder for the user that no sensitive information should be mentioned in this chat 
            and explaination why the information that the user provided is considered sensitive and 
            why it should not be shared.
        """),
    ],
) -> tuple[str, InfoSecUserReminder]:
    """
    If the user mentioned or unknowingly disclosed any sensitive or private information
    relating to the organisation customers or the organisation itself, then it must be
    reported using this function.
    """
    # Note that this logs to current run, not the root run (trace).
    if run := langsmith.get_current_run_tree():
        run.add_tags("user_disclosed_sensitive_information")
        run.add_metadata({"disclosed_sensitive_information_type": information_type})

    content = f"Disclosure of sensitive information type {information_type} was reported."
    artifact = InfoSecUserReminder(message=artifact)
    return content, artifact


class MetaToolkit(BaseToolkit):
    @override
    def get_tools(self) -> list[langchain.tools.BaseTool]:
        tools = [
            report_masked_entities_difficulties,
            report_disclosure_of_sensitive_information,
            report_feedback,
        ]
        return tools

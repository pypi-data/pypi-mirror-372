import inspect
import textwrap
from typing import AsyncGenerator

import bir_mcp
import langchain_core.language_models
import langchain_core.messages
import langgraph.prebuilt

from ai_app.ai_utils import (
    AstreamResponse,
    PreModelHook,
    anonymize_tool_output,
    astream_response_messages,
    trim_history_messages,
)
from ai_app.config import (
    get_anon_codec,
    get_chat_model,
    get_gitlab_toolkit,
    get_jira_toolkit,
    get_sonarqube_toolkit,
)
from ai_app.core import State
from ai_app.pii import EntityTypeCodec, get_sanitized_input_handling_guide
from ai_app.tools import (
    InfoSecUserReminder,
    extract_tool_artifacts_from_agent_response,
    report_disclosure_of_sensitive_information,
    report_feedback,
    report_masked_entities_difficulties,
)


def build_agent(
    model: str | langchain_core.language_models.BaseChatModel, codec: EntityTypeCodec | None = None
):
    model = get_chat_model(model) if isinstance(model, str) else model
    gitlab_toolkit = get_gitlab_toolkit()
    jira_toolkit = get_jira_toolkit()
    jira_tools = jira_toolkit.get_tools()
    jira_tools = [
        anonymize_tool_output(tool, anon_codec=get_anon_codec(), codec=codec) for tool in jira_tools
    ]
    sonarqube_toolkit = get_sonarqube_toolkit()
    tools = (
        gitlab_toolkit.get_tools()
        + sonarqube_toolkit.get_tools()
        + jira_tools
        + [
            # report_disclosure_of_sensitive_information,
            report_masked_entities_difficulties,
            report_feedback,
        ]
    )
    prompt = f"""
        Your job is to evaluate a GitLab merge request. You have tools to fetch details of a merge request by its url 
        and to fetch description of a Jira issue by its key, as well as other tools. Inspect the tool descriptions and call
        them whenever appropriate, preferrably in parallel. You will be provided with a message asking you to review a merge request.
        Additionally, several Jira issues may be provided related to the merge request. You should perform the following steps:
        1. Fetch the details for the GitLab merge request.
        2. If Jira issues were provided by a user or if any Jira issues were mentioned in the merge request title or description, 
        fetch their descriptions and determine whether the issues correlate with the changes in the merge request.
        3. Review the changes in the merge request, evaluate the quality of the code, check for any potential bugs and security issues.
        4. Give a final verdict, whether the merge request is ready to be merged, if not, provide reasons and suggest next actions.
        {get_sanitized_input_handling_guide(codec=codec)}
    """  # noqa: E501
    prompt = textwrap.dedent(prompt)
    prompt = bir_mcp.git_lab.prompts.get_merge_request_review_prompt()
    prompt += f"\nNote about the tool outputs:\n{get_sanitized_input_handling_guide(codec=codec)}"
    prompt += inspect.cleandoc(f"""
        Note about user feedback:
        The user will be asked to provide feedback about the conducted merge request review.
        If you detect any explicit, meaningful feedback, report it via the {report_feedback.name} 
        tool.
    """)

    agent = langgraph.prebuilt.create_react_agent(
        model,
        tools=tools,
        prompt=prompt,
        pre_model_hook=PreModelHook(model=model),
        # By default, providing response format adds an extra call to the model, which is costly.
        # Maybe can be fixed if the structured output is converted to a tool with
        # return_direct=True.
        # response_format=Response,
    )
    return agent


def get_feedback_request_prompt() -> str:
    prompt = textwrap.dedent(
        """

        *If you have any feedback or suggestions regarding this merge request review, please let me know. 
        Your feedback will be used to improve the next version of the review agent.*
        """  # noqa: E501
    )
    return prompt


class Bot:
    # async def respond(
    #     self,
    #     model: langchain_core.language_models.BaseChatModel,
    #     model_input: list[langchain_core.messages.BaseMessage],
    #     codec: EntityTypeCodec | None = None,
    # ) -> str:
    #     agent = build_agent(model, codec=codec)
    #     response: dict = await agent.ainvoke({"messages": model_input})
    #     response_message = response["messages"][-1].content
    #     artifacts = extract_tool_artifacts_from_agent_response(response["messages"])
    #     user_reminders: list[InfoSecUserReminder] | None = artifacts.get(
    #         report_disclosure_of_sensitive_information.name
    #     )
    #     if user_reminders:
    #         user_reminder = user_reminders[0]
    #         response_message = f"**{user_reminder.message}**\n\n{response_message}"

    #     if any(not isinstance(m, langchain_core.messages.AIMessage) for m in model_input):
    #         # If this is the first AI message, ask for feedback.
    #         response_message += get_feedback_request_prompt()

    #     return response_message

    async def astream(
        self,
        model: langchain_core.language_models.BaseChatModel,
        messages: list[langchain_core.messages.BaseMessage],
        state: State,
    ) -> AsyncGenerator[AstreamResponse, None]:
        messages = trim_history_messages(messages)
        agent = build_agent(model, codec=state.codec)
        response = AstreamResponse(formatted_response="", state=[])
        async for response in astream_response_messages(agent, messages, stream_ai_tokens=True):
            yield response

        if all(not isinstance(m, langchain_core.messages.AIMessage) for m in messages):
            yield AstreamResponse(
                response.formatted_response + get_feedback_request_prompt(), response.state
            )

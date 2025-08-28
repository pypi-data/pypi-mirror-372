import inspect
import textwrap

import cachetools.func
import langchain.tools
import langchain_core.messages
import langgraph.prebuilt
import pydantic

from ai_app.ai_utils import PreModelHook, astream_response_messages
from ai_app.apps.jira_service_desk.agent_graph import create_initial_agent
from ai_app.apps.jira_service_desk.data import (
    JiraRequestPrimaryKey,
    get_saved_request_type_primary_keys,
)
from ai_app.apps.jira_service_desk.tools import (
    JiraServiceDeskToolkit,
    build_url_for_jira_request_type,
    fetch_detailed_jira_request_type_guide,
)
from ai_app.config import get_ai_postgres_engine, get_config
from ai_app.core import Response, State
from ai_app.frontend import get_generating_text_span
from ai_app.tools import (
    InfoSecUserReminder,
    build_structured_response_tool,
    extract_tool_artifacts_from_agent_response,
    get_structured_output_from_agent_response,
    report_disclosure_of_sensitive_information,
    report_feedback,
    think,
)


def get_system_prompt() -> str:
    system_prompt = textwrap.dedent(f"""
        # Role
        You are a Jira service desk expert in a bank. Your goal is to help employees find the most 
        appropriate Jira request type for their problem.

        # Language instruction
        - Your primary instruction, above all else, is to detect the language of the user's very 
        last message (Azerbaijani, English, or Russian) and ALWAYS respond in that exact language.
        - DO NOT deviate from this rule, even if other context suggests a different language might be helpful.

        # Steps
        - Use the RAG retriever "{JiraServiceDeskToolkit.fetch_jira_request_type_guides_closest_to_user_query.__name__}" 
        tool to find relevant Jira request types based on the user's messages.
        - Use the "{think.__name__}" tool to plan the next step and determine whether exactly one request type clearly and unambiguously matches
        the user's problem. 
        - If there is no clear standout request type (multiple plausible matches or the message is too vague),
        then ask concise clarifying questions to gather the missing details and narrow down the request type. Otherwise:
            - Call the "{fetch_detailed_jira_request_type_guide.__name__}" tool for the best-matching request type in the same conversation turn.
            - Respond on the first line with a one-sentence recommendation that names the request type and why it fits.
            - On the second line, provide the non-prefilled request type URL from the tool output.
            - Then briefly provide and format three sections:
                - Self-help: how the user may try to resolve the issue independently.
                - Resolution pipeline: how this request is typically handled to resolution.
                - Required information: what is needed to create the request.
        - After finding a relevant request type, in subsequent conversation turns collect from the user the information needed to create 
        a prefilled URL for the suggested request type via the "{build_url_for_jira_request_type.__name__}" 
        tool and provide it to the user. Focus on required fields that can be passed as URL parameters.

        # Guidelines
        - Always call one or several tools, never respond without calling a tool.
        - Proactively ask for user's feedback and use the "{report_feedback.name}" tool to report it, 
        if user provided any explicit feedback.
        - Use the "{build_structured_response_tool(None).name}" tool to generate the message for the user.

        # Examples
        ## Example 1 (clear, unambiguous match):
        User: '''
            I need to report a fraud related to my account.
        '''
        Bot: '''
            The 'Fraud' request type can be used to report suspected fraudulent activity affecting your account or transactions.
            https://jira-support.kapitalbank.az/servicedesk/customer/portal/1/create/1

            ### Self-help
            Immediately lock your card in the mobile app and review recent transactions.
            
            ### Resolution pipeline
            Triage → Transaction review by Fraud Ops → Temporary block if needed → Investigation → Customer notification and resolution.
            
            ### Required information for creating the request
            - Affected account/card
            - Transaction IDs and timestamps
            - Merchant name/location
        '''

        ## Example 2 (ambiguous, needs clarification):
        User: '''
            My card has a problem.
        '''
        Bot: '''
            I found several possible request types 'Card Replacement', 'Card PIN Reset', 'Card Transaction Dispute', could you clarify:
            1. Is the card lost/stolen, damaged, or working but a transaction looks wrong?
            2. If a transaction issue: when did it occur and what merchant?
            3. Do you still have physical possession of the card?
        '''
    """)  # noqa: E501
    return system_prompt


def build_prompts() -> list[langchain_core.messages.BaseMessage]:
    system_prompt = get_system_prompt()
    prompts = [
        langchain_core.messages.SystemMessage(system_prompt),
    ]
    return prompts


class BotResponse(pydantic.BaseModel):
    last_user_message_language: str = pydantic.Field(
        description=inspect.cleandoc("""
            The language of the last user message, which the bot should also use for its own 
            response.
        """),
    )
    content: str = pydantic.Field(description="The message content that the user will see.")


@cachetools.func.ttl_cache(ttl=60)
def get_cached_saved_request_type_primary_keys() -> set[JiraRequestPrimaryKey]:
    return get_saved_request_type_primary_keys(get_ai_postgres_engine())


class Bot:
    def __init__(self, n_closest_requests: int | None = None):
        self.toolkit = JiraServiceDeskToolkit(
            n_closest_requests=n_closest_requests
            or get_config().apps.jira_service_desk.n_closest_requests,
            service_desks=get_config().apps.jira_service_desk.service_desks,
        )

    async def astream(self, model, messages, state: State | None = None):
        if not any(isinstance(m, langchain_core.messages.AIMessage) for m in messages):
            # Initial agent flow can be defined more strictly, since there's less entropy in
            # the conversation state. Also it has more importance and impact than subsequent
            # agent responses, which can be designed as a simple ReAct agent loop.
            agent = create_initial_agent(model, self.toolkit)
        else:
            agent = langgraph.prebuilt.create_react_agent(
                model,
                prompt=get_system_prompt(),
                pre_model_hook=PreModelHook(model=model),
                tools=self.toolkit.get_tools()
                + [
                    # report_disclosure_of_sensitive_information,
                    report_feedback,
                    build_structured_response_tool(BotResponse),
                    langchain.tools.tool(think),  # Add thinking tool for non-reasoning models.
                ],
                response_format=BotResponse,
            )

        response = None
        async for response in astream_response_messages(
            agent, messages, stream_ai_tokens=True, with_spinner=False
        ):
            yield Response(
                content=response.formatted_response + get_generating_text_span(),
                messages=response.state["messages"],
            )

        if not response:
            return

        bot_response = get_structured_output_from_agent_response(response.state)
        yield Response(
            content=response.formatted_response + bot_response.content,
            messages=response.state["messages"],
            content_for_langsmith=bot_response.content,
        )

    async def respond(self, model, messages, state: State | None = None) -> Response:
        response = Response(content="")
        async for response in self.astream(model, messages, state):
            pass

        return response

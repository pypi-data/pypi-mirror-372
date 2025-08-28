import inspect

import langchain_core.messages
import langgraph.graph
import langgraph.prebuilt
import pydantic

from ai_app.apps.jira_service_desk.tools import (
    JiraServiceDeskToolkit,
    fetch_detailed_jira_request_type_guide,
)
from ai_app.tools import build_structured_response_tool, think


async def ainvoke_model_with_tools(
    model,
    tools,
    messages: list[langchain_core.messages.BaseMessage],
    system_prompt: str | None = None,
    tool_choice: str = "any",
) -> list[langchain_core.messages.AIMessage | langchain_core.messages.ToolMessage]:
    model = model.bind_tools(tools, tool_choice=tool_choice)
    if system_prompt:
        messages = [langchain_core.messages.SystemMessage(system_prompt)] + messages

    ai_message = await model.ainvoke(messages)
    tool_messages = await langgraph.prebuilt.ToolNode(tools).ainvoke([ai_message])
    new_messages = [ai_message] + tool_messages
    return new_messages


class BotResponse(pydantic.BaseModel):
    last_user_message_language: str = pydantic.Field(
        description=inspect.cleandoc("""
            The language of the last user message, which the bot should also use for its own 
            response.
        """),
    )
    content: str = pydantic.Field(description="The message content that the user will see.")


def create_initial_agent(model, toolkit: JiraServiceDeskToolkit):
    """Create the agent for first invocation, after which the ReAct agent can be used."""

    async def entrypoint(
        state: langgraph.prebuilt.chat_agent_executor.AgentState,
    ):
        # TODO: can optimize by preemtively call RAG on raw user query,
        # and dropping it if AI decided to rerun it.
        system_prompt = inspect.cleandoc(f"""
            # Role
            You are a Jira service desk expert in a bank. Your goal is to help employees find the most 
            appropriate Jira request type for their problem.

            # Instructions
            Use the RAG retriever "{JiraServiceDeskToolkit.fetch_jira_request_type_guides_closest_to_user_query.__name__}" 
            tool to find relevant Jira request types for user's problem.
        """)  # noqa: E501
        new_messages = await ainvoke_model_with_tools(
            model,
            [toolkit.fetch_jira_request_type_guides_closest_to_user_query],
            state["messages"],
            system_prompt,
        )
        return {"messages": new_messages}

    async def thinking(state: langgraph.prebuilt.chat_agent_executor.AgentState):
        system_prompt = inspect.cleandoc(f"""
            # Role
            You are a Jira service desk expert in a bank. Your goal is to help employees find the most 
            appropriate Jira request type for their problem.

            Use the "{think.__name__}" tool to think and determine whether there is a request type 
            among the retrieved ones that satisfies the following requirements:
            - It clearly and unambiguously matches the user's problem.
            - Other request types are significantly less relevant.

            # Guidelines
            - Keep the reasoning concise and to the point, limit the thoughts to 100 words.
        """)  # noqa: E501
        new_messages = await ainvoke_model_with_tools(
            model,
            [think],
            state["messages"],
            system_prompt,
            tool_choice=think.__name__,
        )
        return {"messages": new_messages}

    async def route(state: langgraph.prebuilt.chat_agent_executor.AgentState):
        system_prompt = inspect.cleandoc(f"""
            # Role
            You are a Jira service desk expert in a bank. Your goal is to help employees find the most 
            appropriate Jira request type for their problem.

            # Choice
            - If there is no clear standout request type, then use the "{build_structured_response_tool(None).name}" tool
            to ask concise clarifying questions to gather the missing details and narrow down the request type. 
            Note that in this case you should detect the language of the user's very 
            last message (Azerbaijani, English, or Russian) and respond in that exact language.
            - Otherwise, call the "{fetch_detailed_jira_request_type_guide.__name__}" tool with the 
            best-matching request type.

            # Guidelines
            - Call exactly one tool out of those provided to you.
        """)  # noqa: E501
        tools = [
            fetch_detailed_jira_request_type_guide,
            build_structured_response_tool(BotResponse),
        ]
        new_messages = await ainvoke_model_with_tools(
            model, tools, state["messages"], system_prompt
        )
        return {"messages": new_messages}

    async def format_request_recommendation(
        state: langgraph.prebuilt.chat_agent_executor.AgentState,
    ):
        system_prompt = inspect.cleandoc(f"""
            # Role
            You are a Jira service desk expert in a bank. Your goal is to help employees find the most 
            appropriate Jira request type for their problem.

            # Language instruction
            - Your primary instruction, above all else, is to detect the language of the user's very 
            last message (Azerbaijani, English, or Russian) and ALWAYS respond in that exact language.
            - DO NOT deviate from this rule, even if other context suggests a different language might be helpful.

            # Output
            - Respond on the first line with a one-sentence recommendation that names the request type and why it fits.
            - On the second line, provide the non-prefilled request type URL from the tool output.
            - Then briefly provide and format three sections:
                - Self-help: how the user may try to resolve the issue independently.
                - Resolution pipeline: how this request is typically handled to resolution.
                - Required information: what is needed to create the request.
            - Proactively ask for user's feedback.
            - Use the "{build_structured_response_tool(None).name}" tool to generate the message for the user.

            # Examples
            ## Example 1
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
        """)  # noqa: E501
        tools = [
            build_structured_response_tool(BotResponse),
        ]
        new_messages = await ainvoke_model_with_tools(
            model, tools, state["messages"], system_prompt
        )
        return {"messages": new_messages}

    def conditional_edge(state: langgraph.prebuilt.chat_agent_executor.AgentState):
        """If response tool was called, return END, otherwise go to format node."""
        last_message = state["messages"][-1]
        if not isinstance(last_message, langchain_core.messages.ToolMessage):
            raise ValueError("Last message is not a tool message.")

        if last_message.name == build_structured_response_tool(None).name:
            return langgraph.graph.END
        else:
            return format_request_recommendation.__name__

    graph = langgraph.graph.StateGraph(langgraph.prebuilt.chat_agent_executor.AgentStatePydantic)
    graph.add_node(entrypoint.__name__, entrypoint)
    graph.add_node(thinking.__name__, thinking)
    graph.add_node(route.__name__, route)
    graph.add_node(format_request_recommendation.__name__, format_request_recommendation)

    graph.set_entry_point(entrypoint.__name__)
    graph.add_edge(entrypoint.__name__, thinking.__name__)
    graph.add_edge(thinking.__name__, route.__name__)
    graph.add_conditional_edges(
        route.__name__,
        conditional_edge,
        # Specify the output nodes for visualization of the graph.
        [
            format_request_recommendation.__name__,
            langgraph.graph.END,
        ],
    )
    graph.set_finish_point(format_request_recommendation.__name__)

    compiled_graph = graph.compile()
    return compiled_graph

import inspect

import gradio as gr
import langchain_core.language_models
import langchain_core.messages
import langgraph.prebuilt

from ai_app.ai_utils import PreModelHook, astream_response_messages
from ai_app.config import get_confluence_toolkit, get_jira_toolkit
from ai_app.core import BaseApp, Response, State
from ai_app.frontend import build_model_choice_dropdown


def get_system_prompt():
    prompt = inspect.cleandoc("""
        # Role and Objective
        You are an IT Governance expert in a bank that can answer questions based on 
        corporate Jira and Confluence.

        # Guidelines
        - You are an agent - please keep going until the user's query is completely resolved, 
        before ending your turn and yielding back to the user.
        - Only terminate your turn when you are sure that the problem is solved.
        - Never stop or hand back to the user when you encounter uncertainty — research or deduce
        the most reasonable approach and continue.
        - Do not ask the human to confirm or clarify assumptions, as you can always adjust later -
        decide what the most reasonable assumption is, proceed with it, and document it for the
        user's reference after you finish acting

        # Output Format
        Use Markdown to format your response.
    """)
    return prompt


class App(BaseApp):
    name = "Governance agent"
    requires_auth = False

    async def astream(
        self,
        model: langchain_core.language_models.BaseChatModel,
        message: langchain_core.messages.BaseMessage,
        frontend_messages: list[langchain_core.messages.BaseMessage],
        state: State,
    ):
        messages = state.messages + [message]
        agent = langgraph.prebuilt.create_react_agent(
            model=model,
            tools=get_jira_toolkit().get_tools() + get_confluence_toolkit().get_tools(),
            pre_model_hook=PreModelHook(model),
            prompt=get_system_prompt(),
        )
        async for response in astream_response_messages(agent, messages, stream_ai_tokens=True):
            yield Response(
                content=response.formatted_response,
                messages=response.state["messages"],
            )

    def build_gradio_blocks(self, model_choice: gr.Dropdown | None = None) -> gr.Blocks:
        with gr.Blocks(fill_height=True) as app:
            model_choice = model_choice or build_model_choice_dropdown()
            self.build_gradio_chat_interface(
                model_choice=model_choice,
                description=("The chatbot can answer questions based on Jira and Confluence"),
                examples=[
                    [
                        "What is the current focus of the ACE Jira project?",
                    ],
                    [
                        "What is Jira project ACE about?",
                    ],
                    [
                        "Which tools do you have access to?",
                    ],
                ],
            )

        return app

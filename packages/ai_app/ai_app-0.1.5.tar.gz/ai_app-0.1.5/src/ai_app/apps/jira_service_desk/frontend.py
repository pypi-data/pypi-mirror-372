import logging
from typing import override

import gradio as gr
import langchain_core.language_models
import langchain_core.messages
import langsmith

from ai_app.apps.jira_service_desk.backend import Bot
from ai_app.config import get_config
from ai_app.core import BaseApp, State
from ai_app.frontend import build_model_choice_dropdown


class App(BaseApp):
    name = "Jira service desk"
    requires_auth = False

    def __init__(self):
        self.bot = Bot()

    async def astream(
        self,
        model: langchain_core.language_models.BaseChatModel,
        message: langchain_core.messages.BaseMessage,
        frontend_messages: list[langchain_core.messages.BaseMessage],
        state: State,
    ):
        messages = state.messages + [message]
        async for response in self.bot.astream(model, messages, state=state):
            yield response

    def like(self, state: State, like_data: gr.LikeData):
        if not state.messages:
            logging.warning("No messages in state to like.")
            return

        if not isinstance(like_data.liked, bool):
            # logging.info(f"Received non-bool like data: {like_data.liked}")
            # like_data.liked can be an empty string when user cancels the like.
            return

        client = langsmith.Client()
        # Index starts from user messages and alternates with AI messages.
        ai_index = like_data.index // 2
        ai_messages = [
            m for m in state.messages if isinstance(m, langchain_core.messages.AIMessage)
        ]
        ai_message = ai_messages[max(ai_index, len(ai_messages) - 1)]
        run_id = ai_message.id.removeprefix("run--").split()[0]
        client.create_feedback(
            run_id=run_id,
            key="user_like",
            score=int(like_data.liked),
        )

    @override
    def build_gradio_blocks(self, model_choice: gr.Dropdown | None = None) -> gr.Blocks:
        with gr.Blocks() as app:
            model_choice = model_choice or build_model_choice_dropdown()
            chat_interface = self.build_gradio_chat_interface(
                model_choice=model_choice,
                description="The chatbot will help the user find appropriate Jira request type.",
                examples=(
                    None
                    if get_config().is_prod
                    else [
                        ["I want to change my password"],
                        ["I need access to a database"],
                        ["I received a phishing email"],
                        ["A system requires additional processing resources"],
                    ]
                ),
            )
            # Registering the event handler enables the flagging buttons.
            chat_interface.chatbot.like(self.like, self.state)

        return app

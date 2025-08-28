import inspect
from typing import override

import gradio as gr
import langchain_core.language_models
import langchain_core.messages

from ai_app.apps.merge_request_review.backend import Bot
from ai_app.core import BaseApp, Response, State


def get_examples():
    examples = [
        """
            https://gitlab.kapitalbank.az/kapitalbankojsc/birbank/birbank-bff/bff-payment-product/-/merge_requests/150
        """,
        """
            https://gitlab.kapitalbank.az/kapitalbankojsc/birbank/birbank-payments/birbank-payments/ms-product-usage/-/merge_requests/4
            https://gitlab.kapitalbank.az/kapitalbankojsc/birbank/consul-config-loader/birbank-payments/consul-config-loader/-/merge_requests/420
        """,
    ]
    examples = [[inspect.cleandoc(e)] for e in examples]  # Convert to Gradio examples format.
    return examples


class App(BaseApp):
    name = "Merge request review"
    requires_auth = False

    def __init__(self):
        self.bot = Bot()

    @override
    async def astream(
        self,
        model: langchain_core.language_models.BaseChatModel,
        message: langchain_core.messages.BaseMessage,
        frontend_messages: list[langchain_core.messages.BaseMessage],
        state: State,
    ):
        messages = state.messages + [message]
        async for response in self.bot.astream(model, messages, state):
            yield Response(content=response.formatted_response, messages=response.state["messages"])

    @override
    def build_gradio_blocks(self, model_choice: gr.Dropdown | None = None) -> gr.Blocks:
        with gr.Blocks(fill_height=True) as app:
            self.build_gradio_chat_interface(
                model_choice=model_choice,
                description="To start the review, provide a GitLab merge request url.",
                examples=get_examples(),
            )

        return app

import inspect
import uuid
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Self

import gradio as gr
import langchain_core.language_models
import langchain_core.messages
import langgraph.errors
import langsmith
import pydantic

from ai_app.config import get_anon_codec, get_chat_model, get_config
from ai_app.frontend import build_model_choice_dropdown
from ai_app.pii import EntityTypeCodec
from ai_app.utils import PydanticForbidExtra


class State(PydanticForbidExtra, arbitrary_types_allowed=True):
    thread_id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)
    name: str | None = None
    email: str | None = None
    messages: list[dict] = []
    codec: EntityTypeCodec = pydantic.Field(
        default_factory=lambda: get_config().build_entity_codec()
    )

    def copy_for_new_conversation(self) -> Self:
        state = State(**self.model_dump(include=["name", "email"]))
        return state

    @property
    def langsmith_extra(self) -> dict:
        langsmith_extra = {"metadata": {"thread_id": self.thread_id}}
        return langsmith_extra

    @classmethod
    def from_request(cls, request: gr.Request) -> Self:
        session = request.request.session
        if user_info := session.get("user_info"):
            state = cls(
                name=user_info.get("name"),
                email=user_info.get("email"),
            )
        else:
            state = cls()

        return state


class Response(pydantic.BaseModel):
    content: str
    additional_outputs: list = []
    messages: list = []
    content_for_langsmith: str | None = pydantic.Field(
        default=None,
        description=inspect.cleandoc("""
            The message to show as agent response in LangSmith UI, 
            which can't render HTML, for example.
        """),
    )


class BaseApp(ABC):
    name: str
    requires_auth: bool

    @abstractmethod
    def build_gradio_blocks(self, model_choice: gr.Dropdown | None = None) -> gr.Blocks: ...

    @classmethod
    def get_api_prefix(cls) -> str:
        api_prefix = cls.name.replace(" ", "_").lower()
        return api_prefix

    @classmethod
    def get_chat_api_name(cls, absolute: bool = False) -> str:
        namespace = "/" if absolute else ""
        api_name = f"{namespace}{cls.get_api_prefix()}_chat"
        return api_name

    async def _respond(
        self,
        message: str,
        conversation: list,
        model_name: str,
        state: State,
        *args,
        **kwargs,
    ):
        # If user cleared the chat or switched to new one in the same interface, need to reset the
        # messages in state also. This would not be necessary if the frontend messages were the
        # single source of truth.
        if not conversation:
            state = state.copy_for_new_conversation()

        model = get_chat_model(model_name)
        message = get_anon_codec().anonymize(message, codec=state.codec)
        message = langchain_core.messages.HumanMessage(message)
        frontend_messages = langchain_core.messages.convert_to_messages(conversation)
        trace = langsmith.trace(
            name=self.name,
            inputs={"message": message},
            metadata={
                "thread_id": state.thread_id,
                "user_name": state.name,
                "user_email": state.email,
            },
        )
        async with trace as run:
            try:
                async for response in self.astream(
                    model, message, frontend_messages, state, *args, **kwargs
                ):
                    state.messages = response.messages
                    yield [response.content] + response.additional_outputs + [state]
            except langgraph.errors.GraphRecursionError:
                raise gr.Error("AI agent exceeded maximum recursion depth.")

            run.add_outputs({"response": response.content_for_langsmith or response.content})

    async def astream(
        self,
        model: langchain_core.language_models.BaseChatModel,
        message: langchain_core.messages.BaseMessage,
        frontend_messages: list[langchain_core.messages.BaseMessage],
        state: State,
        *args,
        **kwargs,
    ) -> AsyncGenerator[Response, None]:
        """Need to be implemented only for apps with chat interface."""
        yield await self.respond(model, message, frontend_messages, state, *args, **kwargs)

    async def respond(
        self,
        model: langchain_core.language_models.BaseChatModel,
        message: langchain_core.messages.BaseMessage,
        frontend_messages: list[langchain_core.messages.BaseMessage],
        state: State,
        *args,
        **kwargs,
    ) -> Response:
        """Need to be implemented only for apps with chat interface."""
        raise NotImplementedError

    def build_gradio_chat_interface(
        self,
        model_choice: gr.Dropdown | None = None,
        additional_inputs: list | None = None,
        additional_outputs: list | None = None,
        **kwargs,
    ) -> gr.ChatInterface:
        model_choice = model_choice or build_model_choice_dropdown()
        self.state = gr.State(State())
        chat_interface = gr.ChatInterface(
            fn=self._respond,
            type="messages",
            additional_inputs=[model_choice, self.state] + (additional_inputs or []),
            additional_outputs=(additional_outputs or []) + [self.state],
            api_name=self.get_chat_api_name(),
            **get_config().common_chat_interface_parameters,
            **kwargs,
        )
        chat_interface.load(State.from_request, outputs=self.state)
        return chat_interface

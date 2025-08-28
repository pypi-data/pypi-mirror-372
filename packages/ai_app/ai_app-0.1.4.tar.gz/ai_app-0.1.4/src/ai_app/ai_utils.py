import contextlib
import datetime
import enum
import functools
import inspect
import json
import logging
import os
import re
import textwrap
import warnings
from typing import Any, AsyncGenerator, Callable, Coroutine, Iterable, NamedTuple

import bir_mcp
import langchain.tools
import langchain_core.language_models
import langchain_core.messages.utils
import langchain_core.prompts
import langsmith
import pydantic

from ai_app.external.providers import get_common_models_meta_attributes
from ai_app.frontend import get_generating_text_span
from ai_app.pii import AnonCodec, EntityTypeCodec
from ai_app.utils import wrap_with_xml_tag


def set_langsmith_environment_variables(
    langsmith_api_key: str,
    langsmith_project: str | None = None,
    langsmith_endpoint: str | None = "https://eu.api.smith.langchain.com",
):
    """
    If LangSmith variables are not set, no errors will be thrown,
    but all logs and traces will be ignored.
    """
    logging.info("Setting LangSmith environment variables")
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_API_KEY"] = langsmith_api_key
    if langsmith_project:
        os.environ["LANGSMITH_PROJECT"] = langsmith_project
    if langsmith_endpoint:
        os.environ["LANGSMITH_ENDPOINT"] = langsmith_endpoint
        os.environ["LANGCHAIN_ENDPOINT"] = langsmith_endpoint


def fetch_root_langsmith_run() -> langsmith.RunTree | None:
    client = langsmith.client.Client()
    run = langsmith.get_current_run_tree()
    if not run:
        return

    root_run = client.read_run(run.trace_id)
    return root_run


class StructuredOutputMethod(enum.StrEnum):
    json_mode = enum.auto()
    json_schema = enum.auto()
    function_calling = enum.auto()


def prepare_llm_input(text: str | None, max_length: int | None = None) -> str:
    """
    Main purpose of this function is to reduce the length of the input to the LLM, while keeping all
    the information.
    """
    if not text:
        return ""

    text = re.sub(" +", " ", text)
    text = re.sub(r"\n+", r"\n", text)
    if max_length:
        text = text[:max_length]

    return text


def invoke_model(
    model,
    prompt_template: langchain_core.prompts.ChatPromptTemplate,
    prompt_params: dict,
    trace: langsmith.trace | None = None,
    max_prompt_param_length: int | None = None,
) -> tuple[Any, str | None]:
    prompt_params = {
        k: prepare_llm_input(v, max_length=max_prompt_param_length)
        for k, v in prompt_params.items()
    }
    with trace if trace else contextlib.nullcontext() as run:
        prompt = prompt_template.invoke(prompt_params)
        model_output = model.invoke(prompt)
        run_id = run.id if run else None

    return model_output, run_id


def to_formatted_markdown(text: str, kind: str = "json") -> str:
    text = f"```{kind}\n{text}\n```"
    return text


def to_json_llm_input(value: dict | list, indent: int | None = 0) -> str:
    string = json_dumps_for_ai(value, indent=indent)
    string = to_formatted_markdown(string)
    return string


def get_pydantic_config_dict_for_openai_structured_output() -> pydantic.ConfigDict:
    """
    https://platform.openai.com/docs/guides/structured-outputs?api-mode=responses#supported-schemas
    There may be ready utilities to transform Pydantic model to OpenAI structured output JSON
    schema, but I haven't found one.
    Another option is to override schema_generator in model_json_schema, but the documentation is
    lacking.
    https://docs.pydantic.dev/latest/api/json_schema/#pydantic.json_schema.GenerateJsonSchema
    """

    def schema_extra(schema: dict, model) -> None:
        for property in schema.get("properties", {}).values():
            property.pop("title", None)
            property.pop("default", None)

    config_dict = pydantic.ConfigDict(
        extra="forbid",
        json_schema_extra=schema_extra,
        json_schema_serialization_defaults_required=False,
    )
    return config_dict


class SummarizationStateBase(pydantic.BaseModel):
    items_summarized: int = pydantic.Field(
        default=0,
        description=inspect.cleandoc("""
            Number of items summarized, a meta field which automatically updates. 
            Should not be provided by the LLM.
        """),
    )


class Summarizer:
    def __init__(self, model, max_tokens: int, context: str | None = None):
        self.model = model
        self.max_tokens = max_tokens
        self.context = (
            "## Summarization context:\n"
            + wrap_with_xml_tag("summarization_context", context, with_new_lines=True)
            if context
            else ""
        )

    def build_prompt(
        self, state: SummarizationStateBase | type[SummarizationStateBase], items: list[str]
    ) -> str:
        current_state = (
            ""
            if isinstance(state, type)
            else f"## Current summarization state:\n{to_json_llm_input(state.model_dump())}\n"
        )
        prompt = (
            textwrap.dedent("""
            ## Task
            Update the summarization state by incorporating information from new items while 
            maintaining consistency with previous data and context.

            ## Instructions
            1. Carefully analyze the current summarization state, context (if any) and new items
            2. Identify key information, patterns, and insights from the new items
            3. Update the state by:
                - Adding new information
                - Refining existing information when new evidence contradicts or enhaces it
                - Maintaining consistency with previous data
                - Take into account the number of items already summarized by the existing state to 
                    estimate how accurate the provided state is, the more items seen, the more 
                    stable and reliable the current state is
            4. Ensure the updated state is:
                - Comprehensive: Covers all important aspects
                - Concise: Avoids redundancy
                - Accurate: Based strictly on the provided data
                - Well-structured: Follows the required output format
            """)
            + f"{current_state}{self.context}\nNew items:\n{to_json_llm_input(items)}\n"
        )
        return prompt

    def update_summarization_state(
        self,
        state: SummarizationStateBase | type[SummarizationStateBase],
        items: list[str],
    ) -> SummarizationStateBase | type[SummarizationStateBase]:
        if not items:
            return state

        if isinstance(state, type):
            state_type = state
            items_summarized = 0
        else:
            state_type = type(state)
            items_summarized = state.items_summarized

        prompt = self.build_prompt(state, items)
        model = self.model.with_structured_output(state_type)
        new_state = model.invoke(prompt)
        new_state.items_summarized = items_summarized + len(items)
        return new_state

    def summarize(
        self, state: SummarizationStateBase | type[SummarizationStateBase], items: list[str]
    ) -> SummarizationStateBase | None:
        """Returns None if no items were provided, otherwise an updated summarization state."""
        item_buffer = []
        for item in items:
            if len(item) > self.max_tokens:
                raise RuntimeError("Item is too large to be summarized.")

            if sum(len(i) for i in item_buffer + [item]) > self.max_tokens:
                state = self.update_summarization_state(state, item_buffer)
                item_buffer = []

            item_buffer.append(item)

        state = self.update_summarization_state(state, item_buffer)
        state = None if isinstance(state, type) else state
        return state


def extract_tool_calls_and_messages(
    messages: list[langchain_core.messages.BaseMessage],
    tool_names: Iterable[str] | None = None,
    only_success: bool = True,
) -> tuple[list[langchain_core.messages.ToolCall], list[langchain_core.messages.ToolMessage]]:
    ai_tool_calls = []
    tool_messages = []
    for message in messages:
        match message:
            case langchain_core.messages.AIMessage(tool_calls=tool_calls):
                ai_tool_calls.extend(tool_calls)
            case langchain_core.messages.ToolMessage(name=name, status=status):
                if only_success and status != "success":
                    continue
                if tool_names and name not in tool_names:
                    continue

                tool_message = langchain_core.messages.ToolMessage(
                    **message.model_dump(include=["content", "name", "tool_call_id"])
                )
                tool_messages.append(tool_message)

    tool_call_ids = {message.tool_call_id for message in tool_messages}
    ai_tool_calls = [call for call in ai_tool_calls if call["id"] in tool_call_ids]
    return ai_tool_calls, tool_messages


def process_nested_basic_datatypes(
    value: str | dict | list | int | None,
    process_string: Callable[[str], str],
):
    """Can be used to recursively process output of a tool, looking for string values."""

    def recursive_process(value):
        match value:
            case str():
                value = process_string(value)
            case dict():
                value = {k: recursive_process(v) for k, v in value.items()}
            case list():
                value = [recursive_process(v) for v in value]

        return value

    value = recursive_process(value)
    return value


def json_dumps_for_ai(value, **kwargs) -> str:
    if not isinstance(value, str):
        value = json.dumps(value, ensure_ascii=False, **kwargs)

    return value


def wrap_with_output_processor(
    function: Callable | Coroutine,
    process_full_output: Callable | None = None,
    process_string: Callable[[str], str] | None = None,
):
    """
    Wrap the function or coroutine to process its ouput before it is passed to the model.
    Useful for model input sanitation or truncation.
    The output of tool will be converted to string.
    """

    def process_output(result) -> str:
        if process_full_output:
            result = process_full_output(result)
        elif process_string:
            result = process_nested_basic_datatypes(result, process_string=process_string)

        result = json_dumps_for_ai(result)
        return result

    @functools.wraps(function)
    async def awrapped(*args, **kwargs):
        result = await function(*args, **kwargs)
        result = process_output(result)
        return result

    @functools.wraps(function)
    def wrapped(*args, **kwargs):
        result = function(*args, **kwargs)
        result = process_output(result)
        return result

    wrap = awrapped if inspect.iscoroutinefunction(function) else wrapped
    return wrap


def render_tool_call(name: str, args: dict, response: str | None = None) -> str:
    args = to_formatted_markdown(json.dumps(args, indent=2, ensure_ascii=False))
    if not response:
        status = "Calling tool"
        response = ""
    else:
        status = "Tool call"
        try:
            response = json.loads(response)
        except json.JSONDecodeError:
            response = to_formatted_markdown(response, kind="text")
        else:
            response = to_formatted_markdown(json.dumps(response, indent=2, ensure_ascii=False))

        response = inspect.cleandoc("""
            **Response:**

            {response}
        """).format(response=response)

    html = textwrap.dedent(
        """
        <details>
        <summary><b>{status} <code>{name}</code></b></summary>
        
        **Arguments:**
        {args}
        {response}
        </details>
        
        """
    ).format(
        status=status,
        name=name,
        args=args,
        response=response,
    )
    return html


class AstreamResponse(NamedTuple):
    formatted_response: str
    state: dict


async def astream_response_messages(
    agent,
    messages: list[langchain_core.messages.BaseMessage],
    stream_ai_tokens: bool = False,
    with_spinner: bool = True,
) -> AsyncGenerator[AstreamResponse, None]:
    """
    Be careful when processsing payloads from different stream modes - depending on
    steam mode generation order, an "update" may be emitted before "values", thus
    leading to inconsistent state, if it depends on both stream modes.
    """
    state = {}
    new_messages: list[langchain_core.messages.BaseMessage] = []
    tool_responses = {}
    formatted_response = ""
    async for stream_mode, payload in agent.astream(
        {"messages": messages},
        stream_mode=["values", "messages", "updates"],
    ):
        match stream_mode:
            case "values":
                state = payload
                continue

            case "messages":
                message, metadata = payload
                if isinstance(message, langchain_core.messages.AIMessageChunk) and message.content:
                    new_messages.append(message)
                else:
                    continue

            case "updates":
                for update_value in payload.values():
                    for message in update_value.get("messages", []):
                        new_messages.append(message)
                        # Cover cases for custom agents, which do not always emit "tools" updates.
                        if isinstance(message, langchain_core.messages.ToolMessage):
                            tool_responses[message.tool_call_id] = message.content

                # Optimization for "tools" node.
                if tools_update := payload.get("tools"):
                    for tool_message in tools_update["messages"]:
                        tool_responses[tool_message.tool_call_id] = tool_message.content

        formatted_messages = []
        for message in new_messages:
            match message:
                case langchain_core.messages.AIMessageChunk() if stream_ai_tokens:
                    formatted_messages.append(message.content)

                case langchain_core.messages.AIMessage():
                    if not stream_ai_tokens:
                        formatted_messages.append(message.content)

                    for tool_call in message.tool_calls:
                        rendered_message = render_tool_call(
                            name=tool_call["name"],
                            args=tool_call["args"],
                            response=tool_responses.get(tool_call["id"]),
                        )
                        formatted_messages.append(rendered_message)

        formatted_response = "".join(formatted_messages)
        yield AstreamResponse(
            formatted_response=formatted_response
            # Do not add spinner if generating AI message chunks.
            + (get_generating_text_span() if with_spinner and stream_mode != "messages" else ""),
            state=state,
        )

    yield AstreamResponse(formatted_response=formatted_response, state=state)


def trim_history_messages(
    messages,
    max_tool_content_len: int = 10_000,
    tool_truncation_placeholder: str = (
        "\n[CONTENT END] The tool output was truncated to reduce the conversation history size. "
        "You can call the tool again to get the full output."
    ),
):
    """
    Should not be used as the pre_model_hook, as then the model will never see the full tool output.
    The tool message trimming is rather straightforward and safe way to reduce the history size.
    For comparison, if deciding to remove tool messages, it is also necessary to remove the tool
    calls so as not to confuse the model and make it think that the tool calls were unsuccessful.
    But when removing tool messages is needed, it is possible to use the
    langchain_core.messages.filter_messages function.
    """
    trimmed_messages = []
    for message in messages:
        match message:
            case langchain_core.messages.ToolMessage():
                message.content = bir_mcp.utils.truncate_text(
                    text=message.content,
                    max_length=max_tool_content_len,
                    placeholder=tool_truncation_placeholder,
                )

        trimmed_messages.append(message)

    return trimmed_messages


class PreModelHook:
    def __init__(
        self,
        model: langchain_core.language_models.BaseChatModel | None = None,
        max_tokens: int | None = None,
    ):
        if model:
            token_counter = model.get_num_tokens_from_messages
            try:
                token_counter([langchain_core.messages.HumanMessage("test")])
            except NotImplementedError:
                token_counter = langchain_core.messages.utils.count_tokens_approximately

        if not max_tokens:
            common_models = get_common_models_meta_attributes()
            if model and model.model_name in common_models:
                max_tokens = common_models[model.model_name].context_window
            else:
                max_tokens = 200_000

        self.token_counter = token_counter
        self.max_tokens = max_tokens

    def __call__(self, state: dict) -> dict:
        trimmed_messages = langchain_core.messages.trim_messages(
            state["messages"],
            token_counter=self.token_counter,
            max_tokens=self.max_tokens,
            start_on="human",
            include_system=True,
            allow_partial=False,
        )
        return {"llm_input_messages": trimmed_messages}


def anonymize_tool_output(
    tool: langchain.tools.StructuredTool, anon_codec: AnonCodec, codec: EntityTypeCodec
) -> langchain.tools.StructuredTool:
    def process_string(value: str) -> str:
        return anon_codec.anonymize(value, codec=codec)

    def wrap(function):
        if not function:
            return

        return wrap_with_output_processor(function, process_string=process_string)

    tool = tool.model_copy()
    tool.func = wrap(tool.func)
    tool.coroutine = wrap(tool.coroutine)
    return tool


def try_converting_to_openai_flex_tier(
    model,
    request_timeout: datetime.timedelta = datetime.timedelta(minutes=15),
):
    """The OpenAI Flex service tier is up to 10x cheaper than the Standard tier."""
    if not model.model_name.startswith("gpt-5") or model.model_name == "o4-mini":
        warnings.warn(f"Model {model.model_name} doesn't support Flex service tier.")
        return model

    model = model.model_copy(
        update={
            "service_tier": "flex",
            "request_timeout": request_timeout.total_seconds(),
        }
    )
    return model

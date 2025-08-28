import langchain.chat_models
import langchain_core
import pydantic

from ai_app.ai_utils import StructuredOutputMethod
from ai_app.external.providers import ModelProvider
from ai_app.utils import PydanticForbidExtra


class ChatModelParameters(PydanticForbidExtra):
    model: str
    model_provider: ModelProvider | None = None
    api_key: pydantic.SecretStr | None = None
    preferred_structured_output_method: StructuredOutputMethod | None = None
    max_possible_completion_tokens: int | None = None

    @classmethod
    def from_model_name(cls, model: str):
        structured_output_method = None
        max_possible_completion_tokens = None
        provider = None
        if model.startswith("gemini"):
            provider = ModelProvider.google_genai
            if model == "gemini-1.5-flash":
                max_possible_completion_tokens = 4096

        elif model.startswith("gpt") or model.startswith("o"):
            provider = ModelProvider.openai
            if model.startswith("gpt-3"):
                structured_output_method = StructuredOutputMethod.function_calling
            else:
                structured_output_method = StructuredOutputMethod.json_schema

            if model == "gpt-4o-mini":
                max_possible_completion_tokens = 16_384

        parameters = cls(
            model_provider=provider,
            model=model,
            preferred_structured_output_method=structured_output_method,
            max_possible_completion_tokens=max_possible_completion_tokens,
        )
        return parameters

    def build_model(
        self, schema=None, max_tokens: int | None = None, **kwargs
    ) -> langchain_core.language_models.BaseChatModel:
        max_tokens = max_tokens or self.max_possible_completion_tokens
        if self.max_possible_completion_tokens:
            max_tokens = min(max_tokens, self.max_possible_completion_tokens)

        model = langchain.chat_models.init_chat_model(
            model=self.model,
            model_provider=self.model_provider,
            api_key=self.api_key,
            max_tokens=max_tokens,
            **kwargs,
        )
        if schema:
            if self.preferred_structured_output_method:
                model = model.with_structured_output(
                    schema, method=self.preferred_structured_output_method
                )
            else:
                model = model.with_structured_output(schema)

        return model

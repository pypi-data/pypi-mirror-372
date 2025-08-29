import dataclasses
import enum
from typing import Iterable

import numpy as np

from ai_app.utils import int_log_2


class ModelProvider(enum.StrEnum):
    openai = enum.auto()
    google_genai = enum.auto()
    azure_openai = enum.auto()


@dataclasses.dataclass
class ModelMetaAttributes:
    name: str
    provider: ModelProvider
    million_input_tokens_cost: float
    million_output_tokens_cost: float
    context_window: int
    supports_system_messages: bool

    @property
    def python_name(self):
        name = self.name.replace("-", "_").replace(".", "_")
        return name

    def get_weighted_cost(self, input_token_weight: float = 10.0):
        cost = np.average(
            [self.million_input_tokens_cost, self.million_output_tokens_cost],
            weights=[input_token_weight, 1],
        )
        return cost

    def get_relative_cost(self, input_token_weight: float = 10.0, lowest_cost=0.25) -> int:
        """
        Returns a relative integer cost >= 1, with each subsequent int signifying a double increase
        in cost.
        """
        cost = self.get_weighted_cost(input_token_weight)
        cost = int_log_2(cost)
        lowest_cost = int_log_2(lowest_cost)
        cost = 1 + max(0, cost - lowest_cost)
        return cost

    def get_relative_cost_representation(self, **kwargs) -> str:
        cost = "💲" * self.get_relative_cost(**kwargs)
        return cost


def get_common_models_meta_attributes() -> dict[str, ModelMetaAttributes]:
    """
    Note that cost depends on token type (input, output, reasoning)
    and on input/output type (text, audio, image, video).
    Pricing is relevant as of 2025.04.23.
    """
    models = [
        ("gemini-2.5-flash", "google_genai", 0.30, 2.50, 1_000_000, True),
        ("gemini-2.5-pro", "google_genai", 1.25, 10.00, 2_000_000, True),
        ("gpt-5", "openai", 1.25, 10.00, 400_000, True),
        ("gpt-5-mini", "openai", 0.25, 2.00, 400_000, True),
        ("gpt-5-nano", "openai", 0.05, 0.40, 400_000, True),
        ("gpt-4.1", "openai", 2.00, 8.00, 1_000_000, True),
        ("gpt-4.1-mini", "openai", 0.40, 1.60, 1_000_000, True),
        ("gpt-4.1-nano", "openai", 0.10, 0.40, 1_000_000, True),
        ("o4-mini", "openai", 1.10, 4.40, 200_000, True),
        ("o3", "openai", 2, 8, 200_000, False),
    ]
    models = [ModelMetaAttributes(*a) for a in models]
    models = sorted(models, key=lambda model: model.get_weighted_cost())
    models = {m.name: m for m in models}
    return models


# ModelName = enum.StrEnum(
#     "ModelName",
#     names=[m.python_name for m in get_common_models_meta_attributes().values()],
# )


def filter_common_model_names(
    max_cost: float = float("inf"),
    supports_system_messages: bool = False,
    providers: Iterable[ModelProvider] | None = None,
) -> list[str]:
    model_names = []
    for name, model in get_common_models_meta_attributes().items():
        if model.get_weighted_cost() > max_cost:
            continue
        if providers and model.provider not in providers:
            continue
        if supports_system_messages and not model.supports_system_messages:
            continue

        model_names.append(name)

    return model_names

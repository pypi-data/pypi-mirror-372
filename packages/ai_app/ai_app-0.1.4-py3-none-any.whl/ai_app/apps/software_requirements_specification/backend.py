import langchain_core
import langsmith
import pydantic

from ai_app.ai_utils import invoke_model
from ai_app.config import get_chat_model


class Characteristic(pydantic.BaseModel):
    feedback: str = pydantic.Field(
        description="Feedback on whether the specification exhibits the characteristic, and why."
    )
    grade: int = pydantic.Field(
        description=(
            "A characteristic grade is an integer value from 1 to 5, where 1 indicates that the specification does not exhibit "
            "the characteristic at all, and 5 indicates sufficient presence of the characteristic."
        )
    )


class Characteristics(pydantic.BaseModel):
    """
    A collection of characteristics that a software requirements specification should exhibit according to the IEEE standard.
    A specification may be graded on each characteristic, resulting in a grade from 1 to 5, along with feedback explaining the grade.
    """

    correct: Characteristic = pydantic.Field(
        description="A specification is correct if every requirement stated therein is one that the software shall meet.",
    )
    unambiguous: Characteristic = pydantic.Field(
        description="A specification is unambiguous if every requirement stated therein has only one interpretation.",
    )
    complete: Characteristic = pydantic.Field(
        description=(
            "A specification is complete if it includes all significant requirements, "
            "whether relating to functionality, performance, design constraints, attributes, or external interfaces."
        ),
    )
    consistent: Characteristic = pydantic.Field(
        description=(
            "A specification is consistent if it does not disagree with some other internal document."
        ),
    )
    ranked_for_importance: Characteristic = pydantic.Field(
        description=(
            "A specification is ranked for importance if each requirement in it has an identifier to indicate either "
            "the importance or stability of that particular requirement."
        ),
    )
    verifiable: Characteristic = pydantic.Field(
        description=(
            "A specification is verifiable if for every requirement stated therein exists some efficient process "
            "with which a person or machine can check that the software product meets the requirement. "
            "In general any ambiguous requirement is not verifiable."
        ),
    )
    modifiable: Characteristic = pydantic.Field(
        description=(
            "A specification is modifiable if its structure and style are such that any changes to the requirements "
            "can be made easily, completely, and consistently while retaining the structure and style."
        ),
    )
    traceable: Characteristic = pydantic.Field(
        description=(
            "A specification is traceable if the origin of each of its requirements is clear and if it facilitates "
            "the referencing of each requirement in future development or enhancement documentation"
        ),
    )


class SoftwareRequirementsSpecificationEvaluation(pydantic.BaseModel):
    """
    A collection of desirable characteristics for a software requirements specification, along with a recommendation
    for improving the specification and an example of such improvements.
    """

    characteristics: Characteristics
    specification_improvement_recommendation: str = pydantic.Field(
        description="A recommendation on how to improve the specification to better adhere to the IEEE standard.",
    )
    specification_improvement_example: str = pydantic.Field(
        description="An example of how to improve the specification, making it follow the IEEE guidelines.",
    )


def build_prompt_template() -> langchain_core.prompts.ChatPromptTemplate:
    prompt_template = langchain_core.prompts.ChatPromptTemplate(
        [
            (
                "system",
                "You are an expert at writing and evaluating software requirements specifications according to the IEEE standard.",
            ),
            (
                "human",
                """
You will be provided with a software requirements specification for a component of a digital banking ecosystem,
which may include sections partially written in Azerbaijani. Your tasks are as follows:
1. Evaluate the specification based on the IEEE standard for software requirements specifications.
2. Assess the specification against a list of characteristics, for each writing short feedback on whether or not the
specification exhibits the characterstic, and assigning an integer value from 1 to 5, where 1 indicates a complete lack
of the characteristic, and 5 indicates a sufficient presence of the characteristic.
3. If possible, suggest improvements for the specification to enhance its characteristics and overall adherence to the IEEE standard.

Here are some guidelines that the specification should follow:
1. Requirements should strictly be about what is needed, independently of the system design, and not how the software should do it.
2. Specification should avoide subjective language, ambiguous adverbs and adjectives, superlatives and negative statements. 
Comparative phrases, non-verifiable terms or terms implying totatily should also be avoided.

Here is the software requirements specification to evaluate:
<specification>{specification}</specification>
                """,
            ),
        ]
    )
    return prompt_template


class SpecificationEvaluator:
    def __init__(
        self,
        max_prompt_param_length: int = 100_000,
        max_completion_tokens: int = 4_000,
        langsmith_trace: str = "Evaluate software requirements specification",
    ):
        self.max_prompt_param_length = max_prompt_param_length
        self.max_completion_tokens = max_completion_tokens
        self.langsmith_trace = langsmith_trace
        self.prompt_template = build_prompt_template()

    def evaluate(
        self, model_name: str, specification: str
    ) -> tuple[SoftwareRequirementsSpecificationEvaluation | None, str]:
        prompt_params = dict(specification=specification)
        model = get_chat_model(model_name)
        model = model.with_structured_output(SoftwareRequirementsSpecificationEvaluation)
        evaluation, run_id = invoke_model(
            model,
            prompt_template=self.prompt_template,
            prompt_params=prompt_params,
            trace=langsmith.trace(self.langsmith_trace),
            max_prompt_param_length=self.max_prompt_param_length,
        )
        return evaluation, run_id

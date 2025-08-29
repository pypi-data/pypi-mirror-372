import datetime
import random
import textwrap
import warnings
from typing import Iterable

import langchain_core
import langsmith.evaluation
import langsmith.schemas
import numpy as np
import prefect
import pydantic
import tqdm.auto

from ai_app.ai_utils import to_json_llm_input, try_converting_to_openai_flex_tier
from ai_app.apps.jira_service_desk.backend import Bot, get_system_prompt
from ai_app.apps.jira_service_desk.data import (
    JiraRequest,
    JiraRequestPrimaryKey,
    ManualJiraRequestGuide,
    fetch_use_case_guides_for_requests,
    get_saved_request_type_primary_keys,
)
from ai_app.apps.jira_service_desk.preparation import generate_requests
from ai_app.config import get_ai_postgres_engine, get_chat_model, get_judge_model_names
from ai_app.core import Response
from ai_app.external.atlassian import build_issue_url
from ai_app.utils import wrap_with_xml_tag


class JiraServiceDeskBotEvaluationExample(pydantic.BaseModel):
    generated_user_query: str
    issue_url: str
    model_used_for_generation: str
    request_type_primary_key: JiraRequestPrimaryKey
    issue_key: str


def generate_evaluation_examples_from_latest_resolved_requests(
    request_primary_key: JiraRequestPrimaryKey,
    limit_requests: int = 1,
) -> Iterable[JiraServiceDeskBotEvaluationExample]:
    requests = list(
        generate_requests(**request_primary_key.model_dump(), limit_requests=limit_requests)
    )
    if len(requests) != limit_requests:
        warnings.warn(
            f"Failed to fetch {limit_requests} requests for primary key {request_primary_key}, "
            f"instead fetched {len(requests)} requests."
        )
        return

    for request in requests:
        issue_key = request["Issue key"]
        judge_model_name = random.choice(get_judge_model_names())
        model = get_chat_model(judge_model_name)
        model = try_converting_to_openai_flex_tier(model)
        system_prompt = textwrap.dedent("""
            We are evaluating a Jira service desk support bot designed to help users find the correct 
            request type and assist with creating and filling out Jira requests. To test the bot, we 
            need realistic synthetic user messages that could have been sent to the bot before a request
            was created.

            **Your task**:

            - Review the provided resolved Jira request in JSON format.
            - Generate a message that a user might have sent to the bot before submitting this request.
            - The message should be natural and reflect how real users communicate: it may contain 
                errors, typos, be brief or incomplete, and written in a hurry.
            - Assume the user knows they are chatting with a bot, so the message is likely direct and 
                to the point, not polite or formal.
            - The message should be in the same language as the request description or comments.
            
            **Produce a single, realistic user message that could have initiated the provided Jira 
            request.**
        """)  # noqa: E501
        response = model.invoke(
            [
                langchain_core.messages.SystemMessage(system_prompt),
                langchain_core.messages.HumanMessage(to_json_llm_input(request)),
            ]
        )
        example = JiraServiceDeskBotEvaluationExample(
            request_type_primary_key=request_primary_key,
            issue_key=issue_key,
            issue_url=build_issue_url(issue_key=issue_key),
            generated_user_query=response.content,
            model_used_for_generation=judge_model_name,
        )
        yield example


def get_or_create_jira_service_desk_dataset(
    dataset_name: str | None = None,
    limit_requests: int = 1,
) -> langsmith.schemas.Dataset:
    dataset_name = dataset_name or f"Jira service desk {datetime.datetime.now():%Y-%m-%d %H:%M:%S}"
    client = langsmith.Client()
    if client.has_dataset(dataset_name=dataset_name):
        dataset = client.read_dataset(dataset_name=dataset_name)
        return dataset

    keys = get_saved_request_type_primary_keys(
        get_ai_postgres_engine(),
        JiraRequest.get_sa_primary_key() == ManualJiraRequestGuide.get_sa_primary_key(),
        ManualJiraRequestGuide.do_recommend,
    )
    examples = []
    for key in tqdm.auto.tqdm(keys):
        for example in generate_evaluation_examples_from_latest_resolved_requests(
            key, limit_requests=limit_requests
        ):
            example = langsmith.schemas.ExampleCreate(
                inputs=example.model_dump(),
                metadata=example.model_dump(include=["model_used_for_generation", "issue_url"]),
            )
            examples.append(example)

    dataset = client.create_dataset(dataset_name=dataset_name)
    client.create_examples(dataset_name=dataset_name, examples=examples)
    return dataset


class JiraServiceDeskBotEvaluation(pydantic.BaseModel):
    evaluation: str = pydantic.Field(
        description=textwrap.dedent("""
            Evaluation of the Jira service desk bot response according to the system prompt.
            All text information should be in English, concise, clear, dry, and to the point.
        """),
    )
    score: float = pydantic.Field(
        description="The score of the Jira service desk bot response, from 0 to 10.",
        ge=0,
        le=10,
    )
    updated_use_case_summary: str | None = pydantic.Field(
        None,
        description=textwrap.dedent("""
            If the bot correctly recommended the request type, then None.
            Otherwise, an updated use case summary, that should include the user's problem, while
            keeping most of content from the original summary.
        """),
    )
    system_prompt_improvement: str | None = pydantic.Field(
        None,
        description=textwrap.dedent("""
            If the bot's system prompt can be meaningfully improved, then provide a concise 
            improvement suggestion.
        """),
    )
    insight: str = pydantic.Field(
        description=textwrap.dedent("""
            A short, actionable insight or conclusion in English following the bot evaluation, for 
            example:
            - If the bot failed to recommend correct request type, why, and how to fix it.
            - How the bot behavior or its context can be improved.
        """),
    )


class Evaluator:
    def __init__(self, judge_model_names: list[str] | None = None):
        self.judge_model_names = judge_model_names or get_judge_model_names()

    def evaluate_example(
        self, inputs: dict, outputs: dict, reference_outputs: dict
    ) -> langsmith.evaluation.EvaluationResults | langsmith.evaluation.EvaluationResult:
        example = JiraServiceDeskBotEvaluationExample(**inputs)
        requests = generate_requests(
            **example.request_type_primary_key.model_dump(),
            jql_filter=f"issue = {example.issue_key}",
        )
        requests = list(requests)
        if len(requests) != 1:
            raise RuntimeError(f"Failed to fetch the Jira request {example.issue_key}.")

        request = requests[0]
        guides = fetch_use_case_guides_for_requests([example.request_type_primary_key])
        if len(guides) > 1:
            raise RuntimeError(
                f"Expected to fetch zero or one guide for request type "
                f"{example.request_type_primary_key}, but fetched {len(guides)} guides."
            )

        guide = None if not guides else guides[0]
        context = {
            "Jira request": request,
            "Use case guide for the Jira request type": guide,
            # "Generated user query": example.generated_user_query,
            "Jira service desk bot conversation": outputs,
        }

        jira_service_desk_system_prompt = wrap_with_xml_tag(
            "jira_service_desk_system_prompt", get_system_prompt(), with_new_lines=True
        )
        system_prompt = textwrap.dedent("""
            # Role
            You are an expert quality assurance specialist evaluating a Jira Service Desk bot.
            Your assessment will help improve the bot's performance and user experience.
            
            # Context
            For evaluation purposes, a real resolved Jira request was taken, and a synthetic user
            message was generated based on this request, with which the user may have come to the
            Jira service desk bot. Then the Jira service desk bot generated a response to this message.
            You will be provided with the following context in JSON format:
            1. The real resolved Jira request.
            2. The complete human and AI conversation with one turn each in LangChain messages format,
            complete with tool calls and responses.
            3. The use case guide for the Jira request type that the bot relies on when deciding 
            which request type to suggest. If the use case guide is of low quality or doesn't cover
            the provided request, it may explain why the bot failed to recommend the correct
            request type.

            # Task
            Your task is to evaluate the quality of the Jira service desk bot response based on the
            following criteria:
            1. High importance:
                - **Adherence to instructions:** The response adheres to the bot's system prompt:
                {jira_service_desk_system_prompt}
            2. Medium importance:
                - **Correctness:** If the user message was not detailed enough for a clear request type
                recommendation, then ensure that the bot asked adequate questions. Otherwise, check
                whether the actual request type is appropriate for the user's query - maybe the resolved
                request type was incorrectly created in the first place. If not, then check
                that the suggested request type is the same as the one in the real resolved request. 
                If the bot suggested a different request type, inspect the context provided to the bot -
                the RAG tool response, and try to understand why the bot failed to recommend the correct 
                request type. Attribute the failure to bot performance, the quality of generated human 
                message, or the mismatch of the RAG tool output.
            3. Low importance:
                - **Relevance:** The response is directly relevant to the user's query.
                - **Clarity:** The response is clear and easy to understand.
                - **Usefulness:** The response provides useful information to the user.
                - **Professionalism:** The response is professional and courteous.
        """).format(jira_service_desk_system_prompt=jira_service_desk_system_prompt)  # noqa: E501
        judge_model_input = [
            langchain_core.messages.SystemMessage(system_prompt),
            langchain_core.messages.HumanMessage(to_json_llm_input(context)),
        ]
        results = []
        score_values = []
        for judge_model_name in self.judge_model_names:
            judge_model = get_chat_model(judge_model_name)
            judge_model = try_converting_to_openai_flex_tier(judge_model)
            judge_model = judge_model.with_structured_output(JiraServiceDeskBotEvaluation)
            evaluation: JiraServiceDeskBotEvaluation = judge_model.invoke(judge_model_input)
            score_values.append(evaluation.score)
            score = langsmith.evaluation.EvaluationResult(
                key=f"Score by {judge_model_name}", score=evaluation.score
            )
            review = langsmith.evaluation.EvaluationResult(
                key=f"Review by {judge_model_name}",
                value="\n\n".join(f"# {k}\n{v}" for k, v in evaluation.model_dump().items()),
            )
            updated_use_case_summary = langsmith.evaluation.EvaluationResult(
                key=f"Updated use case summary by {judge_model_name}",
                value=evaluation.updated_use_case_summary,
            )
            results.extend([score, review, updated_use_case_summary])

        average_result = langsmith.evaluation.EvaluationResult(
            key="Average score", score=np.mean(score_values)
        )
        results.append(average_result)
        results = langsmith.evaluation.EvaluationResults(results=results)
        return results


async def ask_jira_bot(
    example: JiraServiceDeskBotEvaluationExample,
    model_name: str,
    n_closest_requests: int | None = None,
) -> dict:
    user_message = langchain_core.messages.HumanMessage(content=example.generated_user_query)
    bot = Bot(n_closest_requests=n_closest_requests)
    response: Response = await bot.respond(
        model=get_chat_model(model_name),
        messages=[user_message],
    )
    response = {
        # "ai_message": response.content_for_langsmith,
        "langchain_messages": "\n".join(m.pretty_repr() for m in response.messages),
    }
    return response


@prefect.task
async def evaluate_dataset(
    dataset_name: str,
    bot_model_name: str,
    n_closest_requests: int | None = None,
    judge_model_names: list[str] | None = None,
):
    async def process_inputs(inputs: dict) -> dict:
        example = JiraServiceDeskBotEvaluationExample(**inputs)
        response = await ask_jira_bot(
            example=example,
            model_name=bot_model_name,
            n_closest_requests=n_closest_requests,
        )
        return response

    evaluator = Evaluator(judge_model_names=judge_model_names)
    client = langsmith.Client()
    await client.aevaluate(
        process_inputs,
        data=dataset_name,
        evaluators=[evaluator.evaluate_example],
        metadata={
            "Bot model": bot_model_name,
            "Number of closest documents from RAG": n_closest_requests,
        },
    )

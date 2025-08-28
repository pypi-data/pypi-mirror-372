import enum

import atlassian
import gradio as gr
import langchain_core
import langsmith
import pydantic
import requests

from ai_app.config import get_chat_model, get_jira_kwargs
from ai_app.external.atlassian import extract_jira_issue_fields


class ProvidedInformationEvaluation(pydantic.BaseModel):
    """The evaluation of the provided information, how clear, complete and consitent it is, whether or not it enables creation of good manual tests, and why."""

    feedback: str = pydantic.Field(
        description=(
            "The feedback on the quality of the provided information, how clear, complete and consitent it is, "
            "whether or not it enables creation of good manual tests, and why."
        )
    )
    improvement_request: str = pydantic.Field(
        description=(
            "If there is a clear way to improve the quality of the provided information, or if some important information was not provided, "
            "then that information should be included in this improvement request."
        )
    )
    information_quality: int = pydantic.Field(
        description=(
            "The quality of the information provided regarding the Jira issue and what needs to be tested, "
            "on a scale from 1 to 5, where 1 is very poor and 5 is very good."
        )
    )


class JiraTestStep(pydantic.BaseModel):
    """One of the test steps in a sequence of steps comprising the actionable part of the Jira test."""

    purpose: str | None = pydantic.Field(
        default=None, description="One sentence describing the purpose of this test step."
    )
    action: str = pydantic.Field(description="The action that the human tester should perform.")
    expected_result: str = pydantic.Field(description="The expected result following the action.")


class TestType(enum.Enum):
    """The type of a Jira manual test."""

    new_functional = "A functional test that verifies that new features are working as expected."
    smoke_regress = "A preliminary test that quickly checks whether critical functionalities still work after changes."
    smart_regress = "A targeted test that selectively retests the most impacted or high-risk areas of an application."
    full_regress = (
        "A comprehensive test that verifies all existing functionalities of an application."
    )
    draft = "A test category used for cases that do not align with other predefined test types."

    def to_jira_field(self) -> str:
        field = self.name.replace("_", " ").capitalize()
        return field

    @classmethod
    def from_jira_field(cls, test_type: str):
        test_types = {t.to_jira_field(): t for t in TestType}
        test_type = test_types[test_type]
        return cls(test_type)


class JiraTest(pydantic.BaseModel):
    """A manual test related to some Jira issue, meant to verify the quality of whatever the issue represents."""

    title: str = pydantic.Field(description="The title for the test")
    short_description: str = pydantic.Field(
        description=(
            "The description for the test. "
            "If testing a bug, it should include explanation how the test prevents the bug from reoccuring."
            "If testing new features or changes, it should describe how each feature should be tested, "
            "mention possible security vulnerabilities, and assess most likely points of failure and their severity."
        )
    )
    steps: list[JiraTestStep] = pydantic.Field(
        description="The list of approximately 10 test steps that the human tester should manually execute."
    )
    type: TestType = TestType.draft

    def build_creation_fields(self, project: str, assignee_name: str) -> dict:
        steps = [
            {"Action": step.action, "Data": "", "Expected Result": step.expected_result}
            for step in self.steps
        ]
        steps = {"steps": [{"fields": step} for step in steps]}
        parameters = {
            "summary": self.title,
            "description": self.short_description,
            "project": {"key": project},
            "issuetype": {"name": "Test"},
            "assignee": {"name": assignee_name},
            "customfield_18504": steps,
            "customfield_23710": {"value": self.type.to_jira_field()},
        }
        return parameters


class JiraTestWithEvaluation(pydantic.BaseModel):
    evaluation: ProvidedInformationEvaluation
    jira_test: JiraTest


def build_prompt_template():
    prompt_template = langchain_core.prompts.ChatPromptTemplate(
        [
            (
                "system",
                "You are an expert at writing manual tests based on issues in Jira.",
            ),
            (
                "human",
                """
You will be provided with attributes for a single Jira issue, including the issue type, title, and description,
along with an additional prompt that contains specific details and instructions. Some of the information may be
partially written in Azerbaijani. Your tasks are as follows:

1. Evaluate the quality of the provided information. If any information is lacking or unclear, ask for clarification.
2. Rate the quality of the information on a scale from 1 to 5, where 1 represents very poor quality and 5 represents very good quality.
3. Based on the evaluated information, write a manual test for the provided Jira issue:
    - If the Jira issue describes a bug in code or another defect, create a test designed to detect that bug.
    - If the Jira issue describes new features in code, an application, or a user interface, create a test that 
verifies the new features function as expected and that the changes do not introduce any security vulnerabilities or unexpected side effects.

In the context of manual testing, the following abbreviations may be used:
- STR: Steps to reproduce
- AR: Actual result
- ER: Expected result

The output test should include:
- A title
- A description
- A list of test steps, each consisting of a purpose, an action and an expected result for that action

Here are the attributes you will work with:
<jira_issue_type>{issuetype}</jira_issue_type>
<jira_issue_title>{summary}</jira_issue_title>
<jira_issue_description>{description}</jira_issue_description>

And here is the additional prompt from the end user:
<additional_prompt>{additional_prompt}</additional_prompt>
""",
            ),
        ]
    )
    return prompt_template


class JiraTestGenerator:
    def __init__(
        self,
        max_jira_issue_field_length: int = 10_000,
        langsmith_trace: str = "Generate Jira manual test",
    ):
        self.max_jira_issue_field_length = max_jira_issue_field_length
        self.langsmith_trace = langsmith_trace
        self.jira = atlassian.Jira(**get_jira_kwargs())
        self.prompt_template = build_prompt_template()

    def generate(
        self, model_name: str, issue_key: str, additional_prompt: str | None = None
    ) -> tuple[JiraTestWithEvaluation | None, str]:
        try:
            issue = self.jira.get_issue(issue_key, fields="issuetype, summary, description")
        except requests.HTTPError as e:
            raise gr.Error(
                f"Encountered an error when trying to fetch Jira issue '{issue_key}'."
            ) from e

        fields = extract_jira_issue_fields(issue, max_length=self.max_jira_issue_field_length)
        prompt_params = fields | dict(additional_prompt=additional_prompt)
        model = get_chat_model(model_name)
        model = model.with_structured_output(JiraTestWithEvaluation)
        with langsmith.trace(self.langsmith_trace) as run:
            prompt = self.prompt_template.invoke(prompt_params)
            jira_test_with_evaluation = model.invoke(prompt)
            run_id = run.id

        return jira_test_with_evaluation, run_id

    def create_jira_test(self, jira_test: JiraTest, project: str, assignee: str) -> dict:
        fields = jira_test.build_creation_fields(project=project, assignee_name=assignee)
        try:
            issue = self.jira.create_issue(fields=fields)
        except requests.HTTPError as e:
            raise gr.Error("Encountered an error when trying to create a Jira issue.") from e

        return issue

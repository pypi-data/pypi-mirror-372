import uuid
from typing import override

import bidict
import gradio as gr
import pandas as pd
import pydantic

from ai_app.core import BaseApp
from ai_app.external.atlassian import (
    IssueLink,
    build_issue_url,
    fetch_all_jira_project_keys,
    fetch_all_jira_usernames,
)
from ai_app.frontend import build_model_choice_dropdown

from .backend import JiraTest, JiraTestGenerator, JiraTestStep, TestType


class State(pydantic.BaseModel):
    issue_key: str
    run_id: uuid.UUID


def prettify(col: str) -> str:
    col = col.replace("_", " ")
    col = col.capitalize()
    return col


class App(BaseApp):
    name = "Generate Jira manual test"
    requires_auth = False

    def __init__(self):
        self.jira_test_generator = JiraTestGenerator()
        model_fields = list(JiraTestStep.model_fields)
        self.step_columns = [prettify(i) for i in model_fields]
        self.step_field_to_column = bidict.bidict()
        self.step_field_to_column.putall(zip(model_fields, self.step_columns))

    def generate_test(self, model_name: str, issue_key: str, additional_prompt: str):
        jira_test_with_evaluation, run_id = self.jira_test_generator.generate(
            model_name, issue_key, additional_prompt
        )
        if jira_test_with_evaluation is None:
            raise gr.Error("Model couldn't generate a structured Jira test, try different model.")

        evaluation = jira_test_with_evaluation.evaluation
        jira_test = jira_test_with_evaluation.jira_test
        information_quality = gr.BarPlot(
            pd.DataFrame({"Quality": [evaluation.information_quality], "x": ["placeholder"]}),
            y="Quality",
            y_lim=(0, 5),
        )
        steps = pd.DataFrame(jira_test.model_dump()["steps"])
        steps = steps.rename(columns=self.step_field_to_column)
        outputs = [
            information_quality,
            evaluation.feedback,
            evaluation.improvement_request,
            jira_test.title,
            jira_test.short_description,
            jira_test.type.to_jira_field(),
            steps,
            State(issue_key=issue_key, run_id=run_id),
            gr.Button(interactive=True),
        ]
        return outputs

    def create_jira_test(
        self,
        title: str,
        description: str,
        test_type: str,
        steps: pd.DataFrame,
        state: State,
        project: str,
        assignee: str,
        issue_link: str | None,
    ) -> str:
        test_type = TestType.from_jira_field(test_type)
        steps = steps.rename(columns=self.step_field_to_column.inverse)
        steps = steps.to_dict(orient="records")
        steps = [JiraTestStep(**step) for step in steps]
        steps = [step for step in steps if step.action and step.expected_result]
        jira_test = JiraTest(
            title=title, short_description=description, test_type=test_type, steps=steps
        )
        issue = self.jira_test_generator.create_jira_test(
            jira_test=jira_test, project=project, assignee=assignee
        )
        self.jira_test_generator.langsmith_client.create_feedback(
            run_id=state.run_id, key="is_generated_jira_manual_test_used", value=True
        )
        issue_key = issue["key"]
        if issue_link:
            issue_link = IssueLink(issue_link)
            issue_link.link_issues(self.jira_test_generator.jira, issue_key, state.issue_key)

        issue_url = build_issue_url(self.jira_test_generator.jira.url, issue_key)
        markdown_issue_url = f"### <center>{issue_url}</center>"
        return markdown_issue_url

    @override
    def build_gradio_blocks(self, model_choice: gr.Dropdown | None = None) -> gr.Blocks:
        with gr.Blocks() as app:
            gr.Markdown(
                "This app facilitates the creation of Jira manual tests for existing issues using an AI model. "
                "The model will be provided the attributes of an existing issue that you need to test and the additional prompt that you may provide. "
            )
            model_choice = model_choice or build_model_choice_dropdown()
            with gr.Row():
                issue_key = gr.Text(
                    placeholder="PFM-3452",
                    label="Issue key",
                    info="The Jira issue to be tested",
                    min_width=100,
                )
                additional_prompt = gr.TextArea(
                    placeholder="Please write a negative test",
                    label="Additional prompt",
                    info="Any additional instructions for the model, along with extra information needed to generate a quality manual test",
                    max_length=20_000,
                    scale=8,
                    lines=3,
                )

            generate_test = gr.Button("Generate Jira test", variant="primary")
            with gr.Row(variant="compact"):
                evaluation = [
                    gr.BarPlot(pd.DataFrame(), label="Provided data quality", min_width=120),
                    gr.Text(label="Feedback", scale=5),
                    gr.Text(label="Improvement request", scale=5),
                ]

            gr.Markdown("You can modify the generated fields below directly within this app.")
            jira_outputs = [
                gr.Text(label="Test title", interactive=True),
                gr.TextArea(label="Test description", lines=3, interactive=True),
                gr.Dropdown(
                    label="Test type",
                    choices=[i.to_jira_field() for i in TestType],
                    value=TestType.draft.to_jira_field(),
                    interactive=True,
                ),
                gr.Dataframe(
                    label="Test steps",
                    headers=self.step_columns,
                    col_count=(len(self.step_columns), "fixed"),
                    row_count=(3, "dynamic"),
                    datatype=["markdown"],
                    wrap=True,
                    interactive=True,
                ),
                gr.State(),
            ]

            gr.Markdown(
                f"If you're satisfied with the test quality, you can choose the Jira project and assignee "
                f"and create the test in [Jira]({self.jira_test_generator.jira})."
            )
            with gr.Row():
                # Todo: use TTL cache for Jira based function calls.
                project_keys = fetch_all_jira_project_keys(self.jira_test_generator.jira)
                project = gr.Dropdown(project_keys, label="Jira project for the test")
                usernames = fetch_all_jira_usernames(self.jira_test_generator.jira)
                assignee = gr.Dropdown(usernames, label="Jira assignee for the test")
                issue_link = gr.Dropdown(
                    list(IssueLink) + [None], label="Link from the test to the provided issue"
                )
                with gr.Column():
                    create_test = gr.Button(
                        "Create Jira test", variant="primary", interactive=False
                    )
                    created_test_url = gr.Markdown(height=70)
                    create_test.click(
                        self.create_jira_test,
                        inputs=jira_outputs + [project, assignee, issue_link],
                        outputs=created_test_url,
                    )

            generate_test.click(
                self.generate_test,
                inputs=[model_choice, issue_key, additional_prompt],
                outputs=evaluation + jira_outputs + [create_test],
            )

        return app

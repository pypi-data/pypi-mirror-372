import datetime
import inspect
from typing import override

import gradio as gr
import langchain_core.messages
import polars as pl
import pydantic

from ai_app.ai_utils import try_converting_to_openai_flex_tier
from ai_app.config import get_chat_model, get_config
from ai_app.core import BaseApp
from ai_app.external.google import Drive, Spreadsheets, build_drive, build_spreadsheets
from ai_app.frontend import build_model_choice_dropdown
from ai_app.utils import file_to_base64



class PresentationReview(pydantic.BaseModel):
    review: str = pydantic.Field(
        description=inspect.cleandoc("""
            The presentation review with Markdown formatting in the following schema:
            ```
            **Review:**
            <Succinct review tied to rubric criteria>

            **Score:** <score>

            **Suggestions for Improvement:**
            <List of concrete suggestions>
            ```
    """)
    )
    score: int = pydantic.Field(
        ge=1,
        le=5,
        description=inspect.cleandoc("""
            A score from 1 to 5, based on the presentation criteria.
    """),
    )


def get_prompt():
    prompt = inspect.cleandoc("""
        # Role and Objective
        You are an executive presentation reviewer. Your purpose is to strictly, fairly, and 
        consistently assess presentation quality based on clear, business-relevant criteria.

        # Instructions
        First, review the presentation according to the following criteria:
        - Clarity of objectives and scope
        - Business impact, linkage to strategy
        - Evidence/metrics (baselines, changes, ROI, timeframes)
        - Structure/storytelling (problem → approach → results → decisions)
        - Risks, dependencies, blockers
        - Visual effectiveness, communication quality
        - Description of past month results
        - Next month's plans and objectives

        Then, assign a score to the presentation according to the criteria,
        and follow up with specific, actionable suggestions to improve the presentation.

        # Verbosity
        - Keep total response under 200 words.
        - Do not provide extra explanation or context outside the review format.
    """)
    prompt = langchain_core.messages.SystemMessage(prompt)
    return prompt


class App(BaseApp):
    name = "Review presentation"
    requires_auth = False

    def __init__(self):
        self.spreadsheets: Spreadsheets = build_spreadsheets(
            spreadsheet_id="10Pq9Y43_QrU5tU2YCEK39K-q-3RPZDdIVh3GM-dfxnY",
            service_account_info=get_config().secrets.google_service_account_info.get_secret_value(),
        )
        tribes_df = self.spreadsheets.read_sheet("tribes description")
        self.tribes = sorted(set(tribes_df["Tribe"]) - {"Terminated"})
        self.sheet_name = "OKR presentations"
        self.gdrive_folder_id = "1X3jVXMYyNPk2AJtEI3PDmz2080NEucgM"

    def review(self, filepath: str, tribe: str | None, model: str = "gpt-5"):
        # TODO:
        # - Improve prompt, ensure it aligns with criterias.
        # - Be able to process large pdf in chunks.
        prompt = get_prompt()
        message = langchain_core.messages.HumanMessage(
            content=[
                {
                    "type": "file",
                    "mime_type": "application/pdf",
                    "source_type": "base64",
                    "filename": "presentation.pdf",
                    "data": file_to_base64(filepath),
                },
            ]
        )
        model = get_chat_model(model)
        model = try_converting_to_openai_flex_tier(model)
        model = model.with_structured_output(PresentationReview)
        review = model.invoke([prompt, message])

        gdrive: Drive = build_drive(
            get_config().secrets.google_authorized_user_info.get_secret_value()
        )
        url = gdrive.upload(filepath, parents=[self.gdrive_folder_id])

        data = {
            "Date": str(datetime.date.today()),
            "Tribe": tribe,
            "Score": review.score,
            "Reason": review.review,
            "URL": url,
        }
        df = self.spreadsheets.read_sheet(self.sheet_name)
        df = pl.concat([df, pl.DataFrame(data)], how="diagonal_relaxed")
        self.spreadsheets.write_sheet(self.sheet_name, df)
        return review.review, review.score

    @override
    def build_gradio_blocks(self, model_choice: gr.Dropdown | None = None) -> gr.Blocks:
        with gr.Blocks() as app:
            model_choice = model_choice or build_model_choice_dropdown()
            gr.Markdown(
                inspect.cleandoc("""
                Note that gpt-5 will be used for review, and the model dropdown above is ignored.
            """)
            )
            with gr.Row():
                gr.Markdown()  #
                tribe = gr.Dropdown(self.tribes, label="Tribe", value=None)
                review = gr.UploadButton(
                    "Upload a PDF presentation to review",
                    variant="primary",
                    file_types=[".pdf"],
                )
                gr.Markdown()

            gr.Markdown("---\n## Output")
            with gr.Row():
                score = gr.TextArea(label="Score", lines=1, scale=0)
                feedback = gr.Markdown(label="Feedback")

            review.upload(
                self.review,
                inputs=[review, tribe],
                outputs=[feedback, score],
            )

        return app

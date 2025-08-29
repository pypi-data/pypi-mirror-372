from typing import override

import gradio as gr
import pandas as pd

from ai_app.core import BaseApp
from ai_app.frontend import build_model_choice_dropdown

from .backend import SpecificationEvaluator


def prettify(col: str) -> str:
    col = col.replace("_", " ")
    col = col.capitalize()
    return col


class App(BaseApp):
    name = "Evaluate software requirements specification"
    requires_auth = False

    def __init__(self):
        self.specification_evaluator = SpecificationEvaluator()

    def evaluate_software_requirements_specification(self, model_name: str, specification: str):
        evaluation, run_id = self.specification_evaluator.evaluate(
            model_name=model_name, specification=specification
        )
        characteristics = evaluation.characteristics.model_dump()
        characteristics = [
            {
                "Characteristic": prettify(k),
                "Grade": v["grade"],
                "Feedback": v["feedback"],
            }
            for k, v in characteristics.items()
        ]
        characteristics = pd.DataFrame(characteristics)
        characteristics["Grade"] = characteristics["Grade"].clip(1, 5)
        outputs = [
            characteristics,
            evaluation.specification_improvement_recommendation,
            evaluation.specification_improvement_example,
        ]
        return outputs

    @override
    def build_gradio_blocks(self, model_choice: gr.Dropdown | None = None) -> gr.Blocks:
        with gr.Blocks() as app:
            model_choice = model_choice or build_model_choice_dropdown()

            gr.Markdown(
                "This app analyzes software requirement specifications based on the IEEE standard and provides recommendations for improvement"
            )
            specification = gr.TextArea(
                label="Software requirements specification",
                # Remove the value in production.
                value="The App class should implement a range of methods that the frontend is going to call, such as GetCurrentBalance, which takes a timestamp and returns the current balance on all the user accounts.",
            )
            evaluate = gr.Button("Evaluate", variant="primary")
            characteristics = gr.BarPlot(
                pd.DataFrame(),
                label="Desirable specification characteristics",
                x="Characteristic",
                y="Grade",
                y_lim=(0, 5),
                tooltip=["Feedback"],
                title="Hover on a characteristic bar to see detailed feedback",
            )
            recommendation = gr.TextArea(label="Improvement recommendation")
            example = gr.TextArea(label="Improvement example")

            evaluate.click(
                self.evaluate_software_requirements_specification,
                inputs=[model_choice, specification],
                outputs=[characteristics, recommendation, example],
            )

        return app

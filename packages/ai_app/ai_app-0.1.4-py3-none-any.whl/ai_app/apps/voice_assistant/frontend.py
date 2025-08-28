import functools
import textwrap
from typing import override

import gradio as gr
import langchain_core
import langgraph.prebuilt
import pydantic

from ai_app.config import get_config
from ai_app.core import BaseApp
from ai_app.frontend import build_model_choice_dropdown, get_voice_activity_javascript

from .backend import Audio, Retriever, SpeechToTextOpenAI, TextToSpeechOpenAI


def build_prompt_template() -> langchain_core.prompts.ChatPromptTemplate:
    prompt_template = langchain_core.prompts.ChatPromptTemplate(
        [
            {
                "role": "system",
                "content": "You are a telemarketing salesperson at the bank Birbank.",
            },
            {
                "role": "user",
                "content": textwrap.dedent("""
                    You will call a client of Birbank and suggest him some of Birbank products. 
                    Keep your responses short and enthusiastic. Be proactive and try to end your responses with a question. 
                    Your responses will be read aloud, so do not use markdown formatting, numbered or bullet lists.
                    Respond to the user in the same language he speaks.
                    If the user is interested in some Birbank product, suggest to send him a link with product details in a text message.
                    If appropriate, suggest to schedule a visit to the bank for the user to sign the contract.
                """),
                # """
                # Here is the list of available Birbank cards:
                # - Birbank Star: Our new card with a credit line up to 30,000 manats has everything you need,
                # from simplicity and convenience to cashback and 2x VAT refund.
                # - Birbank Cashback: Birbank card will give you up to 30% cashback, free transfer and withdrawal,
                # double VAT and other benefits.
                # - Birbank Umico: It is a unique card jointly presented by Kapital Bank and Umico, designed for daily shopping,
                # combining credit and installment card opportunities and the opportunity to earn additional Umico bonuses.
                # - Birbank Miles: A unique card that gives a bonus of 1 mile per 1 manat for cashless payments with the card,
                # free air travel, interest-free and commission-free installments.
                # - Birbank Umico Premium: It is a unique card jointly presented by Kapital Bank and Umico, designed for daily shopping,
                # combining credit and installment card opportunities and the opportunity to earn additional Umico bonuses.
                # """,
            },
        ]
    )
    return prompt_template


def get_greeting(language: str | None = None) -> str:
    greetings = {
        "az": "Gününüz xeyir! Birbank kredit və debet kartları haqqında bilmək istərdinizmi?",
        "en": "Good day! Would you like to know about Birbank credit and debit cards?",
    }
    greeting = greetings[language or "en"]
    return greeting


class Response(pydantic.BaseModel):
    """The telemarketer model's response, with optional actions to perform."""

    content: str = pydantic.Field(description="The response that the user will see in the chat.")
    offer_details_to_send_to_client: str | None = pydantic.Field(
        default=None,
        description=(
            "The exact offer or product that the user was interested in and requested details about, to be send to him as a text message, "
            "only if the user explicitly asked for them, or consented to receive."
        ),
    )
    schedule_visit: str | None = pydantic.Field(
        default=None,
        description="The time of a visit to the bank that the user asked for or agreed to schedule.",
    )

    def get_events_list(self) -> list[str]:
        events = []
        if self.offer_details_to_send_to_client:
            events.append(f"Send offer details: {self.offer_details_to_send_to_client}")
        if self.schedule_visit:
            events.append(f"Schedule a visit to the bank: {self.schedule_visit}")

        return events


class App(BaseApp):
    """
    Todo:
    - Provide correct "Birbank" pronunciation to TTS models
    - Pass prompt to TTS model with request for intonation and inflection
    - Try to improve latency by trying different sample rates (librosa.resample, pydub.AudioSegment.export), formats (mp3, webm)
    - Greet user only after he said hello

    Resources:
    - https://huggingface.co/spaces/gradio/omni-mini/blob/main/app.py
    - https://github.com/bklieger-groq/gradio-groq-basics/tree/main/calorie-tracker
    """

    name = "Telemarketer"
    requires_auth = False

    def __init__(
        self, speech_to_text_model=None, text_to_speech_model=None, language: str | None = None
    ):
        self.speech_to_text_model = speech_to_text_model or functools.partial(
            SpeechToTextOpenAI().from_audio_sample, language=language
        )
        self.text_to_speech_model = text_to_speech_model or TextToSpeechOpenAI().to_audio_bytes
        self.language = language
        self.prompt_messages = build_prompt_template().invoke({}).messages

    @property
    @functools.cache
    def retriever(self):
        # Lazy initializing heavy class.
        return Retriever()

    def greet(self):
        greeting = get_greeting(language=self.language)
        greeting = [gr.ChatMessage(role="assistant", content=greeting)]
        return greeting

    def speech_to_text(self, audio: tuple, messages: list[dict]):
        audio = Audio(*audio)
        audio = audio.convert_16_bit_wav_to_float()
        text = self.speech_to_text_model(audio)
        message = gr.ChatMessage(role="user", content=text)
        messages.append(message)
        return messages

    def build_agent(self, model_name: str):
        model_parameters = get_config().build_chat_model_parameters(model_name)
        model = model_parameters.build_model()
        agent = langgraph.prebuilt.create_react_agent(
            model, [self.retriever.retrieve_tool], response_format=Response
        )
        return agent

    def respond(self, model_name: str, messages: list[dict], events: str):
        if messages[-1]["role"] == "assistant":
            return [messages, events]

        agent = self.build_agent(model_name)
        output = agent.invoke({"messages": self.prompt_messages + messages})
        response = output["structured_response"]
        new_events = response.get_events_list()
        events = "\n".join([events] + new_events)
        message = gr.ChatMessage(role="assistant", content=response.content)
        messages.append(message)
        return [messages, events]

    def text_to_speech(self, messages):
        if messages[-1]["role"] == "user":
            return

        text = messages[-1]["content"]
        audio = self.text_to_speech_model(text)
        audio = gr.Audio(audio, autoplay=True, recording=False)
        return audio

    def listen(self):
        audio = gr.Audio(None, autoplay=False, recording=True)
        return audio

    @override
    def build_gradio_blocks(self, model_choice: gr.Dropdown | None = None) -> gr.Blocks:
        with gr.Blocks(js=get_voice_activity_javascript()) as app:
            model_choice = model_choice or build_model_choice_dropdown()
            start = gr.Button("Start", variant="primary")
            chatbot = gr.Chatbot(type="messages")
            audio = gr.Audio(sources="microphone", format="wav")
            events = gr.TextArea(label="Events")

            start.click(self.greet, outputs=chatbot)
            chatbot.change(
                self.respond, inputs=[model_choice, chatbot, events], outputs=[chatbot, events]
            ).then(
                self.text_to_speech,
                inputs=chatbot,
                outputs=audio,
            )
            audio.stop_recording(self.speech_to_text, inputs=[audio, chatbot], outputs=chatbot)
            audio.stop(self.listen, outputs=audio)

        return app

import dataclasses
import tempfile
from typing import Iterable

import langchain_chroma
import langchain_community
import langchain_core
import langchain_huggingface
import langchain_text_splitters
import openai
import scipy
import zyphra

from ai_app.config import get_config
from ai_app.utils import wrap_with_xml_tag


def convert_16_bit_wav_to_float(array):
    array = array / 2**15
    return array


@dataclasses.dataclass
class Audio:
    rate: int
    data: Iterable

    def to_tuple(self) -> tuple[int, Iterable[float]]:
        audio = self.rate, self.data
        return audio

    def to_whisper_transformer_format(self) -> dict:
        audio = {"sampling_rate": self.rate, "array": self.data}
        return audio

    def convert_16_bit_wav_to_float(self):
        data = convert_16_bit_wav_to_float(self.data)
        audio = Audio(rate=self.rate, data=data)
        return audio

    def write_wav_to_file(self, file):
        scipy.io.wavfile.write(file, rate=self.rate, data=self.data)

    @classmethod
    def from_wav_file(self, file):
        rate, data = scipy.io.wavfile.read(file)
        audio = Audio(rate=rate, data=data)
        return audio


class SpeechToTextOpenAI:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=get_config().get_provider_api_key("openai"))

    def from_audio_sample(
        self,
        audio: Audio,
        model: str = "whisper-1",
        prompt: str | None = None,
        temperature: float = 0.5,
        language: str | None = None,
        **kwargs,
    ) -> str:
        # OpenAI TTS API expects the file to have a name, as it infers the audio format from the filename suffix,
        # and I haven't found a way to assign a name to io.BytesIO or any non-filesystem object.
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav")
        audio.write_wav_to_file(temp_file)
        temp_file.seek(0)
        transcription = self.openai_client.audio.transcriptions.create(
            file=temp_file.file,
            language=language,
            model=model,
            prompt=prompt,
            temperature=temperature,
            **kwargs,
        )
        text = transcription.text
        return text


class TextToSpeechOpenAI:
    def __init__(self):
        self.client = openai.OpenAI(api_key=get_config().get_provider_api_key("openai"))

    def to_audio_bytes(
        self, text, model: str = "tts-1", voice: str = "alloy", speed: float = 1
    ) -> bytes:
        response = self.client.audio.speech.create(
            input=text,
            model=model,
            voice=voice,
            speed=speed,
            response_format="wav",
        )
        audio_bytes = response.read()
        return audio_bytes


class TextToSpeechZyphra:
    """
    Zyphra has an open source Zonos model, which is available in the zonos package https://github.com/Zyphra/Zonos,
    but I couldn't install it. They also have an API with free tier: https://playground.zyphra.com/
    and a client package: https://pypi.org/project/zyphra/.
    """

    def __init__(self):
        self.api_key = ...  # get_bitwarden_secret("c28a662a-f72f-4bb2-afa1-b28b00a23b2d")

    def to_audio_bytes(self, text, speaking_rate: float = 15.0) -> bytes:
        with zyphra.ZyphraClient(api_key=self.api_key) as client:
            audio_bytes = client.audio.speech.create(
                text=text,
                speaking_rate=speaking_rate,
            )

        return audio_bytes


class Retriever:
    """
    https://python.langchain.com/docs/tutorials/qa_chat_history/
    https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_agentic_rag/
    """

    def __init__(self, directory: str = "data/chroma", document_count_to_retrieve: int = 3):
        embeddings = langchain_huggingface.HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2"
        )
        self.vector_store = langchain_chroma.Chroma(
            embedding_function=embeddings,
            persist_directory=directory,
        )
        self.document_count_to_retrieve = document_count_to_retrieve

        @langchain_core.tools.tool()
        def retrieve(query: str):
            """Retrieve information related to a query."""
            return self.retrieve(query)

        # Todo: be able to directly decorate class methods without the "self" argument being added to function signature.
        self.retrieve_tool = retrieve

    def prepare_data(self):
        loader = langchain_community.document_loaders.WebBaseLoader(
            web_paths=[
                "https://www.kapitalbank.az/en/cards",
                "https://www.kapitalbank.az/en/cards/TaksitCards",
                "https://www.kapitalbank.az/en/cards/simpleCards",
                "https://www.kapitalbank.az/en/cards/GiftCards",
                "https://www.kapitalbank.az/en/cards/studentCard",
                "https://www.kapitalbank.az/en/loans/mikro-biznes-kreditleri",
                # In Azerbaijani:
                # "https://birbank.az",
                # "https://birbank.az/cards/all",
                # "https://birbank.business/en",
                # "https://birbank.business/hesab-xidmetleri",
                # "https://birbank.business/kartlar",
                # "https://birbank.business/kreditler",
                # "https://birbank.business/senedli-emeliyyatlar",
                # "https://birbank.business/elektron-ticaret",
                # "https://birbank.business/pos-xidmetleri",
            ],
        )
        documents = loader.load()
        text_splitter = langchain_text_splitters.RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        document_splits = text_splitter.split_documents(documents)
        self.vector_store.add_documents(documents=document_splits)

    def retrieve(self, query: str):
        documents = self.vector_store.similarity_search(query, k=self.document_count_to_retrieve)
        documents = "\n".join(wrap_with_xml_tag("document", d.page_content) for d in documents)
        return documents

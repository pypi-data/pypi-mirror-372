import contextlib

import gradio as gr
import numpy as np
import torch
import transformers

from .backend import Audio


def get_kokoro_sample_rate_hz():
    """https://github.com/PierrunoYT/Kokoro-TTS-Local/blob/master/README.md#:~:text=Sample%20rate:%2024kHz"""
    return 24_000


class TextToSpeechKokoro:
    """May require the espeak-ng CLI command to be installed."""

    def __init__(self, lang_code: str = "a", device: str = "cpu"):
        """Currently doesn't support mps device."""
        import kokoro  # type: ignore # Requires a lot of extra dependencies to run locally.

        self.pipeline = kokoro.KPipeline(lang_code=lang_code, device=device)

    def generate(
        self,
        text: str | list[str],
        voice: str = "af_heart",
        speed: int = 1,
        split_pattern: str = r"\n+",
    ):
        generator = self.pipeline(
            text,
            voice=voice,
            speed=speed,
            split_pattern=split_pattern,
        )
        for graphemes, phonemes, audio_tensor in generator:
            audio = audio_tensor.numpy()
            yield audio

    def to_audio_sample(self, text, **kwargs) -> Audio:
        audio = list(self.generate(text, **kwargs))
        audio = np.concatenate(audio)
        audio = gr.processing_utils.convert_to_16_bit_wav(audio)
        audio = Audio(rate=get_kokoro_sample_rate_hz(), data=audio)
        return audio


class SpeechToTextWhisper:
    """
    Currently local whisper is 2-3 times slower than OpenAI API,
    but it can be sped up using torch compile, quantization, different Python or C realizations.
    For example, using faster-whisper package (which may need the additional ffmpeg CLI dependency),
    which currently throws an error:

        audio: Audio
        byte_io = io.BytesIO()
        audio.write_wav_to_file(byte_io)
        blob = langchain_core.documents.base.Blob(data=byte_io.read(), mimetype="audio/wav")
        model = langchain_community.document_loaders.parsers.audio.FasterWhisperParser()
        output = model.parse(blob)
    """

    def __init__(
        self,
        device: str = "cpu",
        model_id: str = "openai/whisper-large-v3",
        use_torch_compile: bool = False,
    ):
        torch_dtype = torch.float32 if device == "cpu" else torch.float16
        model = transformers.AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id,
            torch_dtype=torch_dtype,
            low_cpu_mem_usage=True,
            use_safetensors=True,
        )
        model.to(device)

        if use_torch_compile:
            torch.set_float32_matmul_precision("high")

            model.generation_config.cache_implementation = "static"
            model.generation_config.max_new_tokens = 256
            model.forward = torch.compile(model.forward, mode="reduce-overhead", fullgraph=True)

            torch._dynamo.config.suppress_errors = True

        processor = transformers.AutoProcessor.from_pretrained(model_id)
        pipeline = transformers.pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            torch_dtype=torch_dtype,
            device=device,
        )

        self.use_torch_compile = use_torch_compile
        self.model = model
        self.pipeline = pipeline

    def from_audio_sample(self, audio: Audio, language: str | None = None):
        generate_kwargs = {
            "return_timestamps": True,  # To enable processing of audio longer than 30 seconds
            "language": language,  # Specify input language for deterministic results
            # "task": "translate", # To translate input language to English
        }
        if self.use_torch_compile:
            generate_kwargs |= {
                "min_new_tokens": self.model.generation_config.max_new_tokens,
                "max_new_tokens": self.model.generation_config.max_new_tokens,
            }
            context = torch.nn.attention.sdpa_kernel(torch.nn.attention.SDPBackend.MATH)
        else:
            context = contextlib.nullcontext()

        with context:
            output = self.pipeline(
                audio.to_whisper_transformer_format(), generate_kwargs=generate_kwargs
            )

        text = output["text"]
        return text

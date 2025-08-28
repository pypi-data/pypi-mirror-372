import collections
import inspect
import logging
import re
from typing import Iterable, override

import bidict
import httpx
import presidio_analyzer
import presidio_anonymizer
import pydantic

from ai_app.utils import CounterBidict


def get_analyzer_supported_entities(analyzer: presidio_analyzer.AnalyzerEngine) -> list[str]:
    """https://microsoft.github.io/presidio/supported_entities"""
    supported_entities = set()
    for recognizer in analyzer.get_recognizers():
        supported_entities |= set(recognizer.supported_entities)

    return sorted(supported_entities)


class EntityTypeCodec:
    """A statefull class, accumulating seen entities with their assigned ids."""

    def __init__(self, replacing_format: str = "<{entity_type}_{index}>"):
        self.replacing_format = replacing_format
        self.entity_type_counter = collections.defaultdict(CounterBidict)
        self.encoded_entities = bidict.bidict()

    def format_indexed_entity_type(self, entity_type: str, index: int = 0) -> str:
        text = self.replacing_format.format(entity_type=entity_type, index=index)
        return text

    def encode(self, entity_type: str, entity: str) -> str:
        """Operates on an extracted entity string."""
        index = self.entity_type_counter[entity_type][entity]
        encoded_entity = self.format_indexed_entity_type(entity_type=entity_type, index=index)
        self.encoded_entities[entity] = encoded_entity
        return encoded_entity

    def decode(self, encoded_text: str) -> str:
        """Operates on a whole encoded text with multiple encoded entities."""
        if not self.encoded_entities:
            return encoded_text

        decoded_text = re.sub(
            pattern="|".join(self.encoded_entities.values()),
            repl=lambda match: self.encoded_entities.inverse[match.group()],
            string=encoded_text,
        )
        return decoded_text


class CodecOperatorConfig(pydantic.BaseModel, arbitrary_types_allowed=True):
    entity_type: str
    codec: EntityTypeCodec

    def encode(self, entity: str) -> str:
        entity = self.codec.encode(self.entity_type, entity)
        return entity


class EntityCounterOperator(presidio_anonymizer.operators.Operator):
    @override
    @staticmethod
    def operator_name() -> str:
        return "entity_counter"

    @override
    def validate(self, params: dict) -> CodecOperatorConfig | None:
        config = CodecOperatorConfig(**params)
        return config

    @staticmethod
    def build_config(codec):
        config = presidio_anonymizer.OperatorConfig(
            EntityCounterAnonymizer.operator_name(),
            params=dict(codec=codec),
        )
        return config


class EntityCounterAnonymizer(EntityCounterOperator):
    @override
    @staticmethod
    def operator_type() -> presidio_anonymizer.operators.OperatorType:
        return presidio_anonymizer.operators.OperatorType.Anonymize

    @override
    def operate(self, text: str, params: dict) -> str:
        config = self.validate(params)
        anonimized_entity = config.encode(text)
        return anonimized_entity


def build_custom_analyzer(
    deny_list: Iterable[str] | None = None,
) -> presidio_analyzer.AnalyzerEngine:
    # Score is the confidence value from 0 to 1 that the pattern matched something
    # worth anonymizing.
    patterns = [
        presidio_analyzer.Pattern(
            name="AZ_PASSPORT", regex=r"\b(AR|AZ|AZE|AA|MYI|MYİ|MOM|QV|DYI|DYİ)\d{6,}\b", score=0.9
        ),
        presidio_analyzer.Pattern(name="KOD", regex=r"\bKOD ?\d{6,}\b", score=0.9),
        presidio_analyzer.Pattern(name="VOEN", regex=r"\b\d{10}\b", score=0.5),
        # Middle ground between masking senstive numeric ids and too many false positives.
        # Should cover ARN, RRN, account numbers, etc. Doesn't account for spaces in between digits.
        presidio_analyzer.Pattern(name="NUMERIC_ID", regex=r"\b\d{12,}\b", score=0.5),
        presidio_analyzer.Pattern(
            name="ALPHANUMERIC_ID",
            regex=(
                r"\b"
                r"(?=[A-Z0-9]{6,}\b)"  # Look ahead for at least 6 alphanumeric chars.
                r"(?=[0-9]*[A-Z])"  # Look ahead for at least 1 letter.
                r"(?=(?:[A-Z]*[0-9]){2})"  # Look ahead for at least 2 numbers using a non-capturing group.  # noqa: E501
                r"[A-Z0-9]*"  # Consume the chars.
                r"\b"
            ),
            score=0.5,
        ),
    ]
    recognizers = [
        presidio_analyzer.predefined_recognizers.CreditCardRecognizer(),
        presidio_analyzer.predefined_recognizers.CryptoRecognizer(),
        presidio_analyzer.predefined_recognizers.IbanRecognizer(),
        presidio_analyzer.predefined_recognizers.IpRecognizer(),
        presidio_analyzer.predefined_recognizers.MedicalLicenseRecognizer(),
        presidio_analyzer.predefined_recognizers.PhoneRecognizer(),
        *[presidio_analyzer.PatternRecognizer(p.name, patterns=[p]) for p in patterns],
    ]
    if deny_list:
        recognizers.append(presidio_analyzer.PatternRecognizer("SECRET", deny_list=deny_list))

    registry = presidio_analyzer.recognizer_registry.RecognizerRegistry(recognizers=recognizers)
    configuration = {
        "nlp_engine_name": "spacy",
        "models": [
            {"lang_code": "en", "model_name": "en_core_web_md"},
        ],
        "ner_model_configuration": {
            "model_to_presidio_entity_mapping": (
                presidio_analyzer.nlp_engine.ner_model_configuration.MODEL_TO_PRESIDIO_ENTITY_MAPPING
                | {"FAC": "LOCATION"}  # Turn FACility label into LOCATION.
            ),
            "labels_to_ignore": (
                presidio_analyzer.nlp_engine.ner_model_configuration.LABELS_TO_IGNORE
            ),
            "low_score_entity_names": [],
        },
    }
    provider = presidio_analyzer.nlp_engine.NlpEngineProvider(nlp_configuration=configuration)
    nlp_engine = provider.create_engine()
    analyzer = presidio_analyzer.AnalyzerEngine(registry=registry, nlp_engine=nlp_engine)
    return analyzer


class AnonCodec:
    """
    Note that the presence of EntityTypeCodec attribute makes this class stateful when not passing
    custom codec into methods.
    """

    def __init__(
        self,
        analyzer: presidio_analyzer.AnalyzerEngine | None = None,
        codec: EntityTypeCodec | None = None,
        language: str = "en",
        deny_list: Iterable[str] | None = None,
        debug: bool = False,
    ):
        self.analyzer = analyzer or build_custom_analyzer(deny_list=deny_list)
        self.codec = codec or EntityTypeCodec()
        self.language = language
        self.debug = debug
        self.anon_engine = presidio_anonymizer.AnonymizerEngine()
        self.anon_engine.add_anonymizer(EntityCounterAnonymizer)

    def anonymize(
        self, text: str, language: str | None = None, codec: EntityTypeCodec | None = None
    ) -> str:
        codec = codec or EntityTypeCodec()
        analyzer_results = self.analyzer.analyze(text=text, language=language or self.language)
        result = self.anon_engine.anonymize(
            text,
            analyzer_results,
            {"DEFAULT": EntityCounterOperator.build_config(codec)},
        )
        anon_text = result.text
        if self.debug:
            deanon_text = self.deanonymize(anon_text, codec=codec)
            if text != deanon_text:
                logging.warning(f"Non bidirectional anonymization:\n{text}\n---\n{deanon_text}")

        return anon_text

    def deanonymize(self, text: str, codec: EntityTypeCodec) -> str:
        deanon_text = codec.decode(text)
        return deanon_text


def get_sanitized_input_handling_guide(codec: EntityTypeCodec | None = None) -> str:
    """Codec is used to infer the sanitation replacement format the model may encounter"""
    codec = codec or EntityTypeCodec()
    ip_address = codec.format_indexed_entity_type("IP_ADDRESS", 0)
    credit_card = codec.format_indexed_entity_type("CREDIT_CARD", 2)
    guide = inspect.cleandoc(
        f"""
        Some entities in the tool output and messages may be masked due to privacy or security concerns.
        For example, an IP address may be encoded as {ip_address}, and a credit card number as {credit_card}.
        Same encoding corresponds to same entities. You can reference the encodings in your messages, and 
        they will be unmasked for the user to see.
        """  # noqa: E501
    )
    return guide


def call_privacy_guard_api(
    text: str,
    project_key: str,
    url: str = "https://dssapi-data.kapitalbank.az/masker-on-test/public/api/v1/privacy_guard/PI_masker/run",
    timeout: float = 30.0,
    **payload,
) -> httpx.Response:
    """
    Call the Dataiku masking API endpoint.
    https://dssdesign-data.kapitalbank.az/projects/APILIB/api-designer/privacy_guard/endpoints/
    """
    payload |= {
        "text": text,
        "project_key": project_key,
    }
    response = httpx.post(url, timeout=timeout, json=payload)
    return response

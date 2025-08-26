"""
This module provides a Sanitizer class for removing PII and secrets from
text and data structures.
"""

import logging
import re
from typing import Any

import spacy
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider

log = logging.getLogger(__name__)

# Basic regex for finding things that look like keys/secrets
SECRET_REGEXES = {
    "api_key": re.compile(
        r"([a-zA-Z0-9_]*?key[a-zA-Z0-9_]*?)\s*[:=]\s*['\"]?" r"([a-zA-Z0-9_.-]+)['\"]?",
        re.IGNORECASE,
    ),
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "aws_secret_key": re.compile(r"[a-zA-Z0-9/+=]{40}"),
    "github_token": re.compile(r"ghp_[a-zA-Z0-9]{36}"),
    "generic_secret": re.compile(
        r"(['\"]?[a-zA-Z0-9_.-]*secret[a-zA-Z0-9_.-]*['\"]?\s*[:=]\s*"
        r"['\"]?[a-zA-Z0-9_.-]+['\"]?)",
        re.IGNORECASE,
    ),
}


def download_spacy_model_if_not_present(model="en_core_web_sm"):
    """Checks if a spaCy model is available and downloads it if not."""
    try:
        spacy.load(model)
        log.info(f"SpaCy model '{model}' already installed.")
    except OSError:
        log.warning(f"SpaCy model '{model}' not found. Downloading...")
        from spacy.cli.download import download

        download(model)
        log.info(f"Successfully downloaded SpaCy model '{model}'.")


class Sanitizer:
    """Utility to optionally scrub PII/secret-esque tokens.

    By default sanitisation is now **disabled** because Rust crates' public
    metadata should not contain PII.  Pass ``enabled=True`` if you still want
    the behaviour (e.g. for tests).
    """

    def __init__(self, *, enabled: bool = False):
        self.enabled = enabled

        if self.enabled:
            # Heavy-weight models are only loaded if sanitisation requested
            download_spacy_model_if_not_present()

            # Set up Presidio Analyzer
            provider = NlpEngineProvider()
            nlp_engine = provider.create_engine()
            self.analyzer = AnalyzerEngine(
                nlp_engine=nlp_engine, supported_languages=["en"]
            )

    def sanitize_text(self, text: str) -> str:
        """Sanitizes a single string of text."""
        if not isinstance(text, str):
            return text

        if not self.enabled:
            return text

        # PII sanitization
        pii_results = self.analyzer.analyze(text=text, language="en")
        for result in pii_results:
            text = text.replace(
                text[result.start : result.end], f"[{result.entity_type}]"
            )

        # Secret sanitization
        for secret_type, regex in SECRET_REGEXES.items():
            text = regex.sub(f"[{secret_type.upper()}_REDACTED]", text)

        return text

    def sanitize_data(self, data: Any) -> Any:
        """Recursively sanitizes a data structure (dict, list, string)."""
        if not self.enabled:
            return data

        if isinstance(data, dict):
            return {key: self.sanitize_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_data(item) for item in data]
        elif isinstance(data, str):
            return self.sanitize_text(data)
        else:
            return data

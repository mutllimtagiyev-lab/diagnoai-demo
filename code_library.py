"""Read and validate the bundled JSON reference library. Never fetch remote data."""

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


LIBRARY_PATH = Path(__file__).resolve().parent / "data" / "obd_codes.json"


class LocalizedText(BaseModel):
    en: str = Field(min_length=1)
    az: str = Field(min_length=1)

    def in_language(self, language: str) -> str:
        if language not in ("az", "en"):
            raise ValueError("Unsupported language")
        return getattr(self, language)


class Source(BaseModel):
    title: LocalizedText
    url: HttpUrl


class Reference(BaseModel):
    source: str
    location: LocalizedText


class CodeDefinition(BaseModel):
    meaning: LocalizedText
    explanation: LocalizedText
    possible_causes: list[LocalizedText] = Field(min_length=1)
    safe_checks: list[LocalizedText] = Field(min_length=1)
    warnings: list[LocalizedText] = Field(min_length=1)
    urgency: Literal["prompt", "soon"]
    urgency_reason: LocalizedText
    references: list[Reference] = Field(min_length=1)


class CodeLibrary(BaseModel):
    schema_version: Literal[1]
    reviewed_on: str
    sources: dict[str, Source]
    codes: dict[str, CodeDefinition]


def load_library(path: Path = LIBRARY_PATH) -> CodeLibrary:
    library = CodeLibrary.model_validate(json.loads(path.read_text(encoding="utf-8")))
    if "malibu2021" not in library.sources:
        raise ValueError("Missing safety reference in local code library")
    for definition in library.codes.values():
        for reference in definition.references:
            if reference.source not in library.sources:
                raise ValueError("Missing reference in local code library")
    return library

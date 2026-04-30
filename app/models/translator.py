"""Translator and phrasebook models."""
from __future__ import annotations

from pydantic import BaseModel, Field


class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)
    target_language: str = Field(..., min_length=2, max_length=40)
    source_language: str | None = None
    formality: str = Field("neutral", description="casual | neutral | formal")


class PhrasebookEntry(BaseModel):
    english: str
    target: str
    pronunciation: str | None = None
    romanization: str | None = None
    scenario: str
    notes: str | None = None


class Phrasebook(BaseModel):
    target_language: str
    scenarios: list[str]
    entries: list[PhrasebookEntry]
    cultural_tips: list[str] = Field(default_factory=list)
    generated_by: str = "claude-sonnet-4-6"


class TranslationResult(BaseModel):
    request: TranslateRequest
    translation: str
    pronunciation: str | None = None
    romanization: str | None = None
    notes: str | None = None

"""Translator and phrasebook models."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class TranslateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)
    target_language: str = Field(..., min_length=2, max_length=40)
    source_language: Optional[str] = None
    formality: str = Field("neutral", description="casual | neutral | formal")


class PhrasebookEntry(BaseModel):
    english: str
    target: str
    pronunciation: Optional[str] = None
    romanization: Optional[str] = None
    scenario: str
    notes: Optional[str] = None


class Phrasebook(BaseModel):
    target_language: str
    scenarios: List[str]
    entries: List[PhrasebookEntry]
    cultural_tips: List[str] = Field(default_factory=list)
    generated_by: str = "claude-sonnet-4-6"


class TranslationResult(BaseModel):
    request: TranslateRequest
    translation: str
    pronunciation: Optional[str] = None
    romanization: Optional[str] = None
    notes: Optional[str] = None

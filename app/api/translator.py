"""Translator API."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.ai import translator as ai_translator
from app.models.translator import Phrasebook, TranslateRequest, TranslationResult

PREFIX = "/api/translator"
TAGS = ["translator"]
router = APIRouter()


class PhrasebookRequest(BaseModel):
    target_language: str = Field(..., min_length=2)
    scenarios: list[str] = Field(
        default_factory=lambda: ["greetings", "restaurant", "transport", "emergency", "shopping"]
    )


@router.post("/phrasebook", response_model=Phrasebook)
async def phrasebook(req: PhrasebookRequest) -> Phrasebook:
    return ai_translator.phrasebook(req.target_language, req.scenarios)


@router.post("/translate", response_model=TranslationResult)
async def translate(req: TranslateRequest) -> TranslationResult:
    return ai_translator.translate(req)

"""AI-powered translator + phrasebook generator."""
from __future__ import annotations

from app.ai.claude_client import claude_call
from app.models.translator import Phrasebook, PhrasebookEntry, TranslateRequest, TranslationResult

PHRASEBOOK_SYSTEM = """You are a professional travel translator. You produce
practical phrasebooks that include:
- The English phrase
- The accurate translation in the target language (in its native script)
- A romanization (if the script is non-Latin)
- A simple pronunciation hint (English approximation)
- The scenario tag

You generate at least 30 phrases across the requested scenarios, balanced across them.
You include 3-5 cultural tips relevant to courteous communication.

ALWAYS respond with valid JSON only.
"""

TRANSLATE_SYSTEM = """You translate travel phrases. You return: translation, pronunciation,
romanization (if non-Latin script), and brief usage notes if helpful.

ALWAYS respond with valid JSON only.
"""


def _phrasebook_user_prompt(target_language: str, scenarios: list[str]) -> str:
    return f"""Generate a travel phrasebook for: {target_language}

SCENARIOS to cover: {", ".join(scenarios)}

Respond with JSON:
{{
  "entries": [
    {{"english": "...", "target": "...", "pronunciation": "...",
      "romanization": "...", "scenario": "...", "notes": "..."}}
  ],
  "cultural_tips": ["..."]
}}

Generate at least 30 entries spread across all listed scenarios.
"""


def phrasebook(target_language: str, scenarios: list[str]) -> Phrasebook:
    scenarios = scenarios or ["greetings", "restaurant", "transport", "emergency", "shopping"]
    data = claude_call(
        system=PHRASEBOOK_SYSTEM,
        user=_phrasebook_user_prompt(target_language, scenarios),
        max_tokens=3072, json_mode=True,
    )
    entries: list[PhrasebookEntry] = []
    for raw in data.get("entries") or []:
        try:
            entries.append(PhrasebookEntry(
                english=raw.get("english", ""),
                target=raw.get("target", ""),
                pronunciation=raw.get("pronunciation"),
                romanization=raw.get("romanization"),
                scenario=raw.get("scenario", "general"),
                notes=raw.get("notes"),
            ))
        except Exception:
            continue
    return Phrasebook(
        target_language=target_language,
        scenarios=scenarios,
        entries=entries,
        cultural_tips=list(data.get("cultural_tips") or []),
    )


def translate(req: TranslateRequest) -> TranslationResult:
    user = (
        f"Translate this {req.formality} phrase to {req.target_language}: \"{req.text}\""
        + (f" (source language: {req.source_language})" if req.source_language else "")
        + "\n\nReturn JSON: {\"translation\": \"...\", \"pronunciation\": \"...\","
        + " \"romanization\": \"...\", \"notes\": \"...\"}"
    )
    data = claude_call(system=TRANSLATE_SYSTEM, user=user, max_tokens=512, json_mode=True)
    return TranslationResult(
        request=req,
        translation=data.get("translation", ""),
        pronunciation=data.get("pronunciation"),
        romanization=data.get("romanization"),
        notes=data.get("notes"),
    )

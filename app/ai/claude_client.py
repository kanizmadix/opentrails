"""Anthropic Claude client with prompt caching, error mapping, token tracking."""
from __future__ import annotations

import json
import re
from functools import lru_cache
from typing import Any

from app.config import settings
from app.exceptions import ConfigurationError, OpenTrailsError, RateLimitExceeded, UpstreamAPIError
from app.logger import get_logger

log = get_logger(__name__)


@lru_cache(maxsize=1)
def get_client():
    """Singleton anthropic.Anthropic client. Lazy import so tests can patch."""
    if not settings.ANTHROPIC_API_KEY:
        raise ConfigurationError("ANTHROPIC_API_KEY not configured")
    import anthropic
    return anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def _extract_text(message: Any) -> str:
    parts = []
    for block in getattr(message, "content", []) or []:
        text = getattr(block, "text", None)
        if text:
            parts.append(text)
        elif isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))
    return "".join(parts)


def _parse_json(raw: str) -> Any:
    raw = raw.strip()
    if raw.startswith("```"):
        # strip code fences
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    # try direct
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    # find first {...} or [...] span
    match = re.search(r"(\{.*\}|\[.*\])", raw, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    raise ValueError("Could not parse JSON from Claude response")


def claude_call(*, system: str, user: str,
                max_tokens: int | None = None,
                json_mode: bool = False,
                model: str | None = None) -> Any:
    """Single Claude call with prompt caching on system prompt.

    Returns text by default, or parsed JSON when json_mode=True.
    Raises mapped OpenTrailsError subclasses on failure.
    """
    client = get_client()
    model = model or settings.CLAUDE_MODEL
    max_tokens = max_tokens or settings.CLAUDE_MAX_TOKENS

    system_blocks = [{
        "type": "text",
        "text": system,
        "cache_control": {"type": "ephemeral"},
    }]
    user_text = user
    if json_mode:
        user_text += "\n\nRespond ONLY with valid JSON. No prose, no code fences."

    try:
        import anthropic
    except ImportError as exc:  # pragma: no cover
        raise ConfigurationError("anthropic SDK not installed") from exc

    try:
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_blocks,
            messages=[{"role": "user", "content": user_text}],
        )
    except anthropic.AuthenticationError as exc:
        raise ConfigurationError(f"Claude authentication failed: {exc}") from exc
    except anthropic.RateLimitError as exc:
        raise RateLimitExceeded(f"Claude rate limit hit: {exc}") from exc
    except anthropic.APIStatusError as exc:
        raise UpstreamAPIError(f"Claude API status error: {exc}") from exc
    except OpenTrailsError:
        raise
    except Exception as exc:
        raise UpstreamAPIError(f"Claude call failed: {exc}") from exc

    usage = getattr(message, "usage", None)
    if usage is not None:
        log.info(
            "claude_usage",
            model=model,
            input_tokens=getattr(usage, "input_tokens", None),
            output_tokens=getattr(usage, "output_tokens", None),
            cache_read_input_tokens=getattr(usage, "cache_read_input_tokens", None),
            cache_creation_input_tokens=getattr(usage, "cache_creation_input_tokens", None),
        )
    text = _extract_text(message)
    if json_mode:
        try:
            return _parse_json(text)
        except (ValueError, json.JSONDecodeError) as exc:
            raise UpstreamAPIError(f"Claude returned invalid JSON: {exc}") from exc
    return text

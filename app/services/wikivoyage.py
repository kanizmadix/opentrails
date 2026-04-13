"""Wikivoyage destination guide client."""
from __future__ import annotations

from typing import Any
from urllib.parse import quote

from app.config import settings
from app.logger import get_logger
from app.utils.cache import cache
from app.utils.http import get_json

log = get_logger(__name__)

_CACHE_TTL = 60 * 60 * 12  # 12h


async def destination_guide(name: str) -> dict[str, Any]:
    """Fetch summary + related pages from Wikivoyage."""
    if not name:
        return {}
    key = f"wikivoyage:guide:{name}"

    async def _fetch() -> dict[str, Any]:
        summary_url = f"{settings.WIKIVOYAGE_BASE}/page/summary/{quote(name)}"
        related_url = f"{settings.WIKIVOYAGE_BASE}/page/related/{quote(name)}"
        headers = {"User-Agent": settings.USER_AGENT, "Accept": "application/json"}
        try:
            summary = await get_json(summary_url, headers=headers)
        except Exception as exc:
            log.info("wikivoyage_summary_failed", name=name, err=str(exc))
            summary = {}
        try:
            related = await get_json(related_url, headers=headers)
        except Exception:
            related = {}
        return {"summary": summary, "related": related}

    raw = await cache.get_or_set(key, _fetch, ttl=_CACHE_TTL)
    summary = raw.get("summary") or {}
    related = raw.get("related") or {}
    related_pages: list[dict[str, Any]] = []
    for p in (related.get("pages") or [])[:10]:
        related_pages.append({
            "title": p.get("title"),
            "extract": p.get("extract"),
            "url": (p.get("content_urls") or {}).get("desktop", {}).get("page"),
        })
    return {
        "title": summary.get("title") or name,
        "extract": summary.get("extract") or "",
        "url": (summary.get("content_urls") or {}).get("desktop", {}).get("page"),
        "thumbnail": (summary.get("thumbnail") or {}).get("source"),
        "related": related_pages,
    }

"""Wikipedia REST summaries."""
from __future__ import annotations

from typing import Any, Dict
from urllib.parse import quote

from app.config import settings
from app.logger import get_logger
from app.utils.cache import cache
from app.utils.http import get_json

log = get_logger(__name__)

_CACHE_TTL = 60 * 60 * 24  # 24h


async def summary(title: str) -> Dict[str, Any]:
    """Fetch page summary. Returns dict with title, extract, url, image, lat, lon."""
    if not title:
        return {}
    key = f"wikipedia:summary:{title}"

    async def _fetch() -> dict:
        url = f"{settings.WIKIPEDIA_BASE}/page/summary/{quote(title)}"
        return await get_json(url, headers={"User-Agent": settings.USER_AGENT,
                                            "Accept": "application/json"})

    try:
        raw = await cache.get_or_set(key, _fetch, ttl=_CACHE_TTL)
    except Exception as exc:
        log.info("wikipedia_summary_failed", title=title, err=str(exc))
        return {}
    if not isinstance(raw, dict):
        return {}
    coords = raw.get("coordinates") or {}
    return {
        "title": raw.get("title"),
        "extract": raw.get("extract"),
        "url": (raw.get("content_urls") or {}).get("desktop", {}).get("page"),
        "image": (raw.get("thumbnail") or {}).get("source"),
        "lat": coords.get("lat"),
        "lon": coords.get("lon"),
    }


async def extract(title: str) -> str:
    """Convenience: fetch the plain-text extract for a title."""
    data = await summary(title)
    return data.get("extract") or ""

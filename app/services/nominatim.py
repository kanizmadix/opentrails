"""Nominatim (OpenStreetMap) geocoding service. Free, no API key required."""
from __future__ import annotations

from typing import Any, List, Optional

from app.config import settings
from app.exceptions import NotFoundError
from app.logger import get_logger
from app.models.common import GeoPoint, Place
from app.utils.cache import cache
from app.utils.http import get_json

log = get_logger(__name__)

_CACHE_TTL = 60 * 60 * 24  # 24h


def _headers() -> dict:
    return {"User-Agent": settings.USER_AGENT, "Accept-Language": "en"}


async def geocode(query: str, *, limit: int = 5) -> List[Place]:
    """Resolve a free-text query to candidate Places."""
    if not query or not query.strip():
        return []
    key = f"nominatim:geocode:{query.lower().strip()}:{limit}"

    async def _fetch() -> List[dict]:
        url = f"{settings.NOMINATIM_BASE}/search"
        params = {
            "q": query,
            "format": "json",
            "addressdetails": 1,
            "limit": limit,
            "extratags": 1,
        }
        return await get_json(url, params=params, headers=_headers())

    raw: List[dict] = await cache.get_or_set(key, _fetch, ttl=_CACHE_TTL)
    return [_to_place(item) for item in raw]


async def reverse(lat: float, lon: float) -> Optional[Place]:
    """Reverse geocode a coordinate to a Place."""
    key = f"nominatim:reverse:{round(lat, 4)}:{round(lon, 4)}"

    async def _fetch() -> dict:
        url = f"{settings.NOMINATIM_BASE}/reverse"
        params = {"lat": lat, "lon": lon, "format": "json", "addressdetails": 1}
        return await get_json(url, params=params, headers=_headers())

    raw: Any = await cache.get_or_set(key, _fetch, ttl=_CACHE_TTL)
    if not raw or "error" in raw:
        return None
    return _to_place(raw)


async def geocode_one(query: str) -> Place:
    """Geocode and raise NotFoundError if no match."""
    matches = await geocode(query, limit=1)
    if not matches:
        raise NotFoundError(f"No location found for '{query}'")
    return matches[0]


def _to_place(item: dict) -> Place:
    addr = item.get("address") or {}
    return Place(
        name=item.get("display_name") or item.get("name") or "",
        country=addr.get("country"),
        country_code=(addr.get("country_code") or "").upper() or None,
        region=addr.get("state") or addr.get("region"),
        geo=GeoPoint(lat=float(item["lat"]), lon=float(item["lon"])) if "lat" in item else None,
        osm_id=int(item["osm_id"]) if item.get("osm_id") else None,
        wikidata_id=(item.get("extratags") or {}).get("wikidata"),
    )

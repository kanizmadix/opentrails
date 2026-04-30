"""Overpass API client for OpenStreetMap POI queries (free, no key)."""
from __future__ import annotations

from collections.abc import Iterable

from app.config import settings
from app.logger import get_logger
from app.utils.cache import cache
from app.utils.http import post_json

log = get_logger(__name__)

_CACHE_TTL = 60 * 60  # 1h

# Mapping of friendly category names to OSM tag selectors.
CATEGORY_TAGS: dict[str, list[str]] = {
    "tourism": ["tourism=attraction", "tourism=museum", "tourism=viewpoint", "tourism=artwork"],
    "historic": ["historic"],
    "museum": ["tourism=museum"],
    "park": ["leisure=park", "boundary=national_park"],
    "nature": ["natural=peak", "natural=waterfall", "natural=beach"],
    "beach": ["natural=beach", "leisure=beach_resort"],
    "religious": ["amenity=place_of_worship"],
    "food": ["amenity=restaurant", "amenity=cafe"],
    "shopping": ["shop=mall", "shop=department_store"],
    "viewpoint": ["tourism=viewpoint"],
    "entertainment": ["amenity=theatre", "amenity=cinema", "leisure=amusement_arcade"],
    "nightlife": ["amenity=bar", "amenity=pub", "amenity=nightclub"],
}


def _build_query(bbox: tuple[float, float, float, float], categories: Iterable[str]) -> str:
    south, west, north, east = bbox
    selectors: list[str] = []
    for cat in categories or ["tourism"]:
        for tag in CATEGORY_TAGS.get(cat, [f"tourism={cat}"]):
            if "=" in tag:
                k, v = tag.split("=", 1)
                selectors.append(f'  node["{k}"="{v}"]({south},{west},{north},{east});')
                selectors.append(f'  way["{k}"="{v}"]({south},{west},{north},{east});')
            else:
                selectors.append(f'  node["{tag}"]({south},{west},{north},{east});')
                selectors.append(f'  way["{tag}"]({south},{west},{north},{east});')
    body = "\n".join(selectors)
    return f"[out:json][timeout:25];\n(\n{body}\n);\nout center 100;"


async def query_pois(bbox: tuple[float, float, float, float],
                     categories: Iterable[str] | None = None) -> list[dict]:
    """Query POIs in a bounding box (south, west, north, east)."""
    cats = list(categories or ["tourism"])
    cache_key = f"overpass:{bbox}:{','.join(sorted(cats))}"

    async def _fetch() -> dict:
        ql = _build_query(bbox, cats)
        return await post_json(
            settings.OVERPASS_BASE,
            data={"data": ql},
            headers={"Content-Type": "application/x-www-form-urlencoded",
                     "User-Agent": settings.USER_AGENT},
        )

    raw = await cache.get_or_set(cache_key, _fetch, ttl=_CACHE_TTL)
    if not isinstance(raw, dict):
        return []
    out: list[dict] = []
    for el in raw.get("elements", []):
        tags = el.get("tags") or {}
        name = tags.get("name") or tags.get("name:en")
        if not name:
            continue
        lat = el.get("lat") or (el.get("center") or {}).get("lat")
        lon = el.get("lon") or (el.get("center") or {}).get("lon")
        if lat is None or lon is None:
            continue
        out.append({
            "id": f"{el.get('type', 'node')}/{el.get('id')}",
            "name": name,
            "lat": float(lat),
            "lon": float(lon),
            "tags": tags,
        })
    return out

"""OpenTripMap POI service. Falls back to Overpass+Wikipedia if no API key."""
from __future__ import annotations

from typing import List, Optional

from app.config import settings
from app.logger import get_logger
from app.models.attractions import Attraction, AttractionCategory, AttractionDetail
from app.models.common import GeoPoint
from app.services import overpass, wikipedia
from app.utils.cache import cache
from app.utils.http import get_json

log = get_logger(__name__)

_CACHE_TTL = 60 * 60 * 6  # 6h


_KIND_TO_CATEGORY: dict[str, AttractionCategory] = {
    "historic": AttractionCategory.HISTORIC,
    "museums": AttractionCategory.MUSEUM,
    "museum": AttractionCategory.MUSEUM,
    "natural": AttractionCategory.NATURE,
    "beaches": AttractionCategory.BEACH,
    "religion": AttractionCategory.RELIGIOUS,
    "amusements": AttractionCategory.ENTERTAINMENT,
    "shops": AttractionCategory.SHOPPING,
    "foods": AttractionCategory.FOOD,
    "view_points": AttractionCategory.VIEWPOINT,
    "architecture": AttractionCategory.ARCHITECTURE,
    "parks": AttractionCategory.PARK,
}


def _classify(kinds_str: str) -> AttractionCategory:
    if not kinds_str:
        return AttractionCategory.OTHER
    for kind in kinds_str.split(","):
        cat = _KIND_TO_CATEGORY.get(kind.strip())
        if cat:
            return cat
    return AttractionCategory.OTHER


def _has_key() -> bool:
    return bool(settings.OPENTRIPMAP_API_KEY)


async def pois_radius(lat: float, lon: float, *, radius_m: int = 2000,
                      kinds: Optional[List[str]] = None, limit: int = 30,
                      min_rate: int = 0) -> List[Attraction]:
    """Search POIs within radius. Falls back to Overpass when API key absent."""
    if _has_key():
        return await _otm_pois_radius(lat, lon, radius_m=radius_m, kinds=kinds,
                                      limit=limit, min_rate=min_rate)
    return await _fallback_pois_radius(lat, lon, radius_m=radius_m, kinds=kinds, limit=limit)


async def _otm_pois_radius(lat: float, lon: float, *, radius_m: int, kinds: Optional[List[str]],
                           limit: int, min_rate: int) -> List[Attraction]:
    kinds_str = ",".join(kinds) if kinds else "interesting_places"
    cache_key = f"otm:radius:{lat:.3f}:{lon:.3f}:{radius_m}:{kinds_str}:{limit}:{min_rate}"

    async def _fetch() -> dict:
        url = f"{settings.OPENTRIPMAP_BASE}/en/places/radius"
        params = {
            "radius": radius_m, "lon": lon, "lat": lat,
            "kinds": kinds_str, "format": "json", "limit": limit,
            "rate": min_rate, "apikey": settings.OPENTRIPMAP_API_KEY,
        }
        return await get_json(url, params=params)

    raw = await cache.get_or_set(cache_key, _fetch, ttl=_CACHE_TTL)
    if not isinstance(raw, list):
        return []
    out: List[Attraction] = []
    for item in raw:
        name = item.get("name")
        if not name:
            continue
        out.append(Attraction(
            xid=item.get("xid") or f"otm:{item.get('osm') or name}",
            name=name,
            geo=GeoPoint(lat=float(item.get("point", {}).get("lat", lat)),
                         lon=float(item.get("point", {}).get("lon", lon))),
            category=_classify(item.get("kinds", "")),
            rate=int(item.get("rate") or 0) or None,
            distance_m=item.get("dist"),
            wikidata_id=item.get("wikidata"),
            osm_id=str(item.get("osm")) if item.get("osm") else None,
            kinds=[k.strip() for k in (item.get("kinds") or "").split(",") if k.strip()],
        ))
    return out


async def _fallback_pois_radius(lat: float, lon: float, *, radius_m: int,
                                kinds: Optional[List[str]], limit: int) -> List[Attraction]:
    deg = max(radius_m / 111000.0, 0.005)
    bbox = (lat - deg, lon - deg, lat + deg, lon + deg)
    cats = kinds or ["tourism", "historic", "museum"]
    pois = await overpass.query_pois(bbox, categories=cats)
    out: List[Attraction] = []
    for p in pois[:limit]:
        tags = p.get("tags", {})
        kinds_list = [f"{k}={v}" for k, v in tags.items()
                      if k in {"tourism", "historic", "leisure", "natural", "amenity"}]
        out.append(Attraction(
            xid=p["id"],
            name=p["name"],
            geo=GeoPoint(lat=p["lat"], lon=p["lon"]),
            category=_classify_tags(tags),
            osm_id=p["id"],
            kinds=kinds_list,
            wikidata_id=tags.get("wikidata"),
        ))
    return out


def _classify_tags(tags: dict) -> AttractionCategory:
    if "historic" in tags:
        return AttractionCategory.HISTORIC
    if tags.get("tourism") == "museum":
        return AttractionCategory.MUSEUM
    if tags.get("tourism") == "viewpoint":
        return AttractionCategory.VIEWPOINT
    if tags.get("amenity") == "place_of_worship":
        return AttractionCategory.RELIGIOUS
    if "natural" in tags or "leisure" in tags:
        return AttractionCategory.NATURE
    return AttractionCategory.OTHER


async def poi_detail(xid: str) -> AttractionDetail:
    """Fetch detailed POI info. Uses OTM if keyed; otherwise Wikipedia summary."""
    if _has_key() and xid.startswith(("Q", "R", "W", "N")):
        cache_key = f"otm:detail:{xid}"

        async def _fetch() -> dict:
            url = f"{settings.OPENTRIPMAP_BASE}/en/places/xid/{xid}"
            return await get_json(url, params={"apikey": settings.OPENTRIPMAP_API_KEY})

        raw = await cache.get_or_set(cache_key, _fetch, ttl=_CACHE_TTL)
        if isinstance(raw, dict):
            return _otm_detail(raw)
    # fallback: try wikipedia summary
    summary = await wikipedia.summary(xid.split("/")[-1])
    return AttractionDetail(
        xid=xid,
        name=summary.get("title") or xid,
        geo=GeoPoint(lat=summary.get("lat", 0.0), lon=summary.get("lon", 0.0))
        if summary.get("lat") else GeoPoint(lat=0.0, lon=0.0),
        category=AttractionCategory.OTHER,
        description=summary.get("extract"),
        wikipedia_url=summary.get("url"),
        image_url=summary.get("image"),
    )


def _otm_detail(raw: dict) -> AttractionDetail:
    point = raw.get("point") or {}
    info = raw.get("info") or {}
    addr = raw.get("address") or {}
    address_str = ", ".join(filter(None, [addr.get("road"), addr.get("city"), addr.get("country")]))
    return AttractionDetail(
        xid=raw.get("xid", ""),
        name=raw.get("name") or "",
        geo=GeoPoint(lat=float(point.get("lat", 0.0)), lon=float(point.get("lon", 0.0))),
        category=_classify(raw.get("kinds", "")),
        description=info.get("descr") or raw.get("wikipedia_extracts", {}).get("text"),
        image_url=raw.get("preview", {}).get("source"),
        wikipedia_url=raw.get("wikipedia"),
        address=address_str or None,
        kinds=[k.strip() for k in (raw.get("kinds") or "").split(",") if k.strip()],
    )

"""REST Countries client. Free, no API key."""
from __future__ import annotations

from app.config import settings
from app.exceptions import NotFoundError
from app.logger import get_logger
from app.models.destinations import CountryProfile
from app.utils.cache import cache
from app.utils.http import get_json

log = get_logger(__name__)

_CACHE_TTL = 60 * 60 * 24  # 24h

_FIELDS = "name,cca2,cca3,capital,region,subregion,population,area,languages,currencies,timezones,flag,flags,idd,car"


async def country(code_or_name: str) -> CountryProfile:
    """Lookup country by alpha-2/3 or partial name."""
    key = f"restcountries:lookup:{code_or_name.lower()}"

    async def _fetch() -> list[dict]:
        # Try alpha code first when 2-3 chars
        if len(code_or_name) in (2, 3):
            url = f"{settings.REST_COUNTRIES_BASE}/alpha/{code_or_name}"
            params = {"fields": _FIELDS}
        else:
            url = f"{settings.REST_COUNTRIES_BASE}/name/{code_or_name}"
            params = {"fields": _FIELDS}
        result = await get_json(url, params=params)
        if isinstance(result, dict):
            return [result]
        return result or []

    raw = await cache.get_or_set(key, _fetch, ttl=_CACHE_TTL)
    if not raw:
        raise NotFoundError(f"Country '{code_or_name}' not found")
    return _to_profile(raw[0])


async def all_countries() -> list[CountryProfile]:
    """List all countries (lightweight projection)."""
    key = "restcountries:all"

    async def _fetch() -> list[dict]:
        url = f"{settings.REST_COUNTRIES_BASE}/all"
        return await get_json(url, params={"fields": _FIELDS})

    raw = await cache.get_or_set(key, _fetch, ttl=_CACHE_TTL)
    return [_to_profile(item) for item in raw or []]


def _to_profile(raw: dict) -> CountryProfile:
    name = (raw.get("name") or {}).get("common") or raw.get("name") or ""
    official = (raw.get("name") or {}).get("official")
    capital_list = raw.get("capital") or []
    idd = raw.get("idd") or {}
    calling_code: str | None = None
    if idd.get("root"):
        suffixes = idd.get("suffixes") or [""]
        calling_code = f"{idd['root']}{suffixes[0] if suffixes else ''}"
    car = raw.get("car") or {}
    return CountryProfile(
        name=name,
        official_name=official,
        code_alpha2=raw.get("cca2"),
        code_alpha3=raw.get("cca3"),
        capital=capital_list[0] if capital_list else None,
        region=raw.get("region"),
        subregion=raw.get("subregion"),
        population=raw.get("population"),
        area_km2=raw.get("area"),
        languages=raw.get("languages") or {},
        currencies=raw.get("currencies") or {},
        timezones=raw.get("timezones") or [],
        flag_emoji=raw.get("flag"),
        flag_svg=(raw.get("flags") or {}).get("svg"),
        calling_code=calling_code,
        drives_on=car.get("side"),
    )

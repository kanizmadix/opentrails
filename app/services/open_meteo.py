"""Open-Meteo weather forecast and historical climate. Free, no API key."""
from __future__ import annotations

from typing import Any

from app.config import settings
from app.logger import get_logger
from app.models.destinations import WeatherSummary
from app.utils.cache import cache
from app.utils.http import get_json

log = get_logger(__name__)

_CACHE_TTL_FORECAST = 60 * 60 * 3  # 3h
_CACHE_TTL_CLIMATE = 60 * 60 * 24  # 24h


async def forecast(lat: float, lon: float, *, days: int = 7) -> WeatherSummary:
    """Daily forecast for the next `days` days."""
    days = max(1, min(days, 16))
    key = f"open-meteo:forecast:{lat:.3f}:{lon:.3f}:{days}"

    async def _fetch() -> dict[str, Any]:
        url = f"{settings.OPEN_METEO_BASE}/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code",
            "timezone": "auto",
            "forecast_days": days,
        }
        return await get_json(url, params=params)

    raw = await cache.get_or_set(key, _fetch, ttl=_CACHE_TTL_FORECAST)
    return _summarize(raw)


async def historical_climate(lat: float, lon: float) -> WeatherSummary:
    """Coarse climate normals using ERA5 monthly aggregation (last full year)."""
    key = f"open-meteo:climate:{lat:.3f}:{lon:.3f}"

    async def _fetch() -> dict[str, Any]:
        url = f"{settings.OPEN_METEO_BASE.replace('api.open-meteo.com', 'archive-api.open-meteo.com')}/archive"
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "auto",
        }
        return await get_json(url, params=params)

    raw = await cache.get_or_set(key, _fetch, ttl=_CACHE_TTL_CLIMATE)
    return _summarize(raw)


def _summarize(raw: dict[str, Any]) -> WeatherSummary:
    daily = raw.get("daily") or {}
    highs = [float(x) for x in (daily.get("temperature_2m_max") or []) if x is not None]
    lows = [float(x) for x in (daily.get("temperature_2m_min") or []) if x is not None]
    precip = [float(x) for x in (daily.get("precipitation_sum") or []) if x is not None]
    dates = list(daily.get("time") or [])
    avg_high = round(sum(highs) / len(highs), 1) if highs else None
    avg_low = round(sum(lows) / len(lows), 1) if lows else None
    rainy_days = sum(1 for p in precip if p > 1.0) if precip else None
    summary = None
    if avg_high is not None and avg_low is not None:
        summary = f"Average highs around {avg_high}°C, lows around {avg_low}°C"
        if rainy_days:
            summary += f", {rainy_days} days with notable rain"
    return WeatherSummary(
        daily_high_c=highs,
        daily_low_c=lows,
        daily_precip_mm=precip,
        dates=dates,
        avg_high_c=avg_high,
        avg_low_c=avg_low,
        rainy_days=rainy_days,
        summary=summary,
    )

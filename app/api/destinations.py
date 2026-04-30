"""Destination intel API."""
from __future__ import annotations

from fastapi import APIRouter, Query

from app.ai import destination_intel
from app.models.common import Place
from app.models.destinations import DestinationIntel, WeatherSummary
from app.services import frankfurter, nominatim, open_meteo, rest_countries, wikivoyage

PREFIX = "/api/destinations"
TAGS = ["destinations"]
router = APIRouter()


@router.get("/search", response_model=list[Place])
async def search(q: str = Query(..., min_length=1)) -> list[Place]:
    return await nominatim.geocode(q, limit=8)


@router.get("/weather", response_model=WeatherSummary)
async def weather(lat: float = Query(..., ge=-90, le=90),
                  lon: float = Query(..., ge=-180, le=180),
                  days: int = Query(7, ge=1, le=16)) -> WeatherSummary:
    return await open_meteo.forecast(lat, lon, days=days)


@router.get("/currency")
async def currency(from_: str = Query(..., alias="from"),
                   to: str = Query(...),
                   amount: float = Query(1.0, gt=0)) -> dict:
    return await frankfurter.convert(from_, to, amount=amount)


@router.get("/{country_code}/intel", response_model=DestinationIntel)
async def intel(country_code: str) -> DestinationIntel:
    country = await rest_countries.country(country_code)
    place = await nominatim.geocode_one(country.name)
    weather_summary = WeatherSummary()
    if place.geo:
        weather_summary = await open_meteo.forecast(place.geo.lat, place.geo.lon, days=7)
    wv = await wikivoyage.destination_guide(country.name)
    try:
        return destination_intel.compile_intel(country, wv, weather_summary)
    except Exception:
        return DestinationIntel(country=country, weather=weather_summary,
                                summary=(wv or {}).get("extract"),
                                wikivoyage_url=(wv or {}).get("url"))

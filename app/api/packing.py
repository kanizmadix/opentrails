"""Packing list API."""
from __future__ import annotations

from fastapi import APIRouter

from app.ai import packing_list
from app.models.destinations import CountryProfile, WeatherSummary
from app.models.packing import PackingList, PackingRequest
from app.services import nominatim, open_meteo, rest_countries

PREFIX = "/api/packing"
TAGS = ["packing"]
router = APIRouter()


@router.post("/generate", response_model=PackingList)
async def generate(req: PackingRequest) -> PackingList:
    place = await nominatim.geocode_one(req.destination)
    weather = WeatherSummary()
    country = CountryProfile(name=place.country or req.destination,
                             code_alpha2=place.country_code)
    if place.geo:
        weather = await open_meteo.forecast(place.geo.lat, place.geo.lon,
                                            days=min((req.end_date - req.start_date).days + 1, 16))
    if place.country_code:
        try:
            country = await rest_countries.country(place.country_code)
        except Exception:
            pass
    return packing_list.generate_packing(req, weather, country)

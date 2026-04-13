"""Itinerary planner API."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.ai import itinerary_builder
from app.models.destinations import WeatherSummary
from app.models.itinerary import DayPlan, ItineraryRequest, ItineraryResponse
from app.services import nominatim, open_meteo, providers
from app.storage import itineraries as itin_storage
from app.storage import trips as trips_storage

PREFIX = "/api/itinerary"
TAGS = ["itinerary"]
router = APIRouter()


@router.post("/generate", response_model=ItineraryResponse)
async def generate(req: ItineraryRequest) -> ItineraryResponse:
    place = await nominatim.geocode_one(req.destination)
    weather = WeatherSummary()
    attractions = []
    if place.geo:
        weather = await open_meteo.forecast(place.geo.lat, place.geo.lon,
                                            days=min((req.end_date - req.start_date).days + 1, 16))
        attractions, _ = await providers.search_attractions(
            lat=place.geo.lat, lon=place.geo.lon, radius_m=8000, limit=30,
        )
    return itinerary_builder.build_itinerary(req, attractions, weather)


@router.post("/save")
async def save(trip_id: int, itinerary: ItineraryResponse) -> dict:
    trips_storage.get_trip(trip_id)  # 404 if missing
    ids = itin_storage.save_itinerary(trip_id, itinerary)
    return {"trip_id": trip_id, "saved_day_ids": ids, "count": len(ids)}


@router.get("/trip/{trip_id}", response_model=list[DayPlan])
async def for_trip(trip_id: int) -> list[DayPlan]:
    trips_storage.get_trip(trip_id)
    plans = itin_storage.list_for_trip(trip_id)
    if not plans:
        raise HTTPException(status_code=404, detail=f"No itinerary saved for trip {trip_id}")
    return plans

"""Trip CRUD API."""
from __future__ import annotations

from fastapi import APIRouter, status

from app.models.trips import TripCreate, TripRecord, TripUpdate
from app.storage import trips as trips_storage

PREFIX = "/api/trips"
TAGS = ["trips"]
router = APIRouter()


@router.post("", response_model=TripRecord, status_code=status.HTTP_201_CREATED)
async def create(payload: TripCreate) -> TripRecord:
    return trips_storage.create_trip(payload)


@router.get("", response_model=list[TripRecord])
async def list_(limit: int = 50, offset: int = 0) -> list[TripRecord]:
    return trips_storage.list_trips(limit=limit, offset=offset)


@router.get("/{trip_id}", response_model=TripRecord)
async def get(trip_id: int) -> TripRecord:
    return trips_storage.get_trip(trip_id)


@router.patch("/{trip_id}", response_model=TripRecord)
async def update(trip_id: int, payload: TripUpdate) -> TripRecord:
    return trips_storage.update_trip(trip_id, payload)


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(trip_id: int) -> None:
    trips_storage.delete_trip(trip_id)

"""Tests for trip storage CRUD."""
from __future__ import annotations

from datetime import date

import pytest

from app.exceptions import NotFoundError
from app.models.trips import TripCreate, TripUpdate
from app.storage import trips as trips_storage


def test_create_and_get_trip():
    rec = trips_storage.create_trip(TripCreate(
        name="Tokyo Adventure", origin="JFK", destination="Tokyo",
        start_date=date(2026, 6, 1), end_date=date(2026, 6, 8),
        travelers=2, budget_usd=3500.0,
    ))
    assert rec.id > 0
    assert rec.name == "Tokyo Adventure"
    fetched = trips_storage.get_trip(rec.id)
    assert fetched.destination == "Tokyo"


def test_list_trips_returns_in_order():
    a = trips_storage.create_trip(TripCreate(name="A", destination="A"))
    b = trips_storage.create_trip(TripCreate(name="B", destination="B"))
    rows = trips_storage.list_trips()
    ids = [r.id for r in rows]
    assert a.id in ids and b.id in ids


def test_update_trip_partial():
    rec = trips_storage.create_trip(TripCreate(name="Trip", destination="Bali"))
    updated = trips_storage.update_trip(rec.id, TripUpdate(notes="Honeymoon", travelers=2))
    assert updated.notes == "Honeymoon"
    assert updated.travelers == 2
    assert updated.destination == "Bali"


def test_delete_trip_then_404():
    rec = trips_storage.create_trip(TripCreate(name="Trip", destination="Lima"))
    trips_storage.delete_trip(rec.id)
    with pytest.raises(NotFoundError):
        trips_storage.get_trip(rec.id)


def test_get_unknown_raises():
    with pytest.raises(NotFoundError):
        trips_storage.get_trip(99999)

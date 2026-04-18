"""Tests for trips CRUD API."""
from __future__ import annotations


def test_trip_crud_full_cycle(app_client, disable_rate_limit):
    create = app_client.post("/api/trips", json={
        "name": "Spain Tour", "destination": "Madrid",
        "travelers": 2, "budget_usd": 2500.0,
    })
    assert create.status_code == 201, create.text
    trip = create.json()
    trip_id = trip["id"]

    listing = app_client.get("/api/trips")
    assert listing.status_code == 200
    assert any(t["id"] == trip_id for t in listing.json())

    fetched = app_client.get(f"/api/trips/{trip_id}")
    assert fetched.status_code == 200
    assert fetched.json()["destination"] == "Madrid"

    updated = app_client.patch(f"/api/trips/{trip_id}", json={"notes": "Tapas focus"})
    assert updated.status_code == 200
    assert updated.json()["notes"] == "Tapas focus"

    deleted = app_client.delete(f"/api/trips/{trip_id}")
    assert deleted.status_code == 204

    missing = app_client.get(f"/api/trips/{trip_id}")
    assert missing.status_code == 404

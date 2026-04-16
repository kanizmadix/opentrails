"""Tests for the provider router fallback logic."""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from app.models.flights import FlightSearchRequest
from app.models.hotels import HotelSearchRequest
from app.services import providers


@pytest.mark.asyncio
async def test_search_flights_falls_back_to_mock_without_keys():
    req = FlightSearchRequest(
        origin="JFK", destination="CDG",
        departure_date=date.today() + timedelta(days=10),
        adults=1, max_results=3,
    )
    resp = await providers.search_flights(req)
    assert resp.provider == "mock"
    assert len(resp.offers) > 0
    assert resp.cheapest is not None
    assert resp.cheapest.price.total.amount > 0


@pytest.mark.asyncio
async def test_search_hotels_falls_back_to_mock_without_keys():
    today = date.today()
    req = HotelSearchRequest(
        city="PAR", check_in=today + timedelta(days=10),
        check_out=today + timedelta(days=13), adults=2, max_results=3,
    )
    resp = await providers.search_hotels(req)
    assert resp.provider == "mock"
    assert len(resp.offers) > 0
    assert resp.offers[0].nightly_price.amount > 0


@pytest.mark.asyncio
async def test_search_attractions_returns_mock_when_no_data(monkeypatch):
    async def fake_overpass(*args, **kwargs):
        return []
    monkeypatch.setattr("app.services.opentripmap.overpass.query_pois", fake_overpass)

    items, provider = await providers.search_attractions(
        lat=48.85, lon=2.35, radius_m=2000, limit=5,
    )
    assert provider in ("mock",)
    assert len(items) > 0

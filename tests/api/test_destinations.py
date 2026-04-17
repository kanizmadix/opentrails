"""Tests for destinations API (mocked upstream)."""
from __future__ import annotations

import pytest
import respx
from httpx import Response

from app.config import settings


@respx.mock
def test_destinations_search(app_client, disable_rate_limit):
    respx.get(f"{settings.NOMINATIM_BASE}/search").mock(
        return_value=Response(200, json=[{
            "display_name": "Bali, Indonesia", "lat": "-8.34", "lon": "115.09",
            "address": {"country": "Indonesia", "country_code": "id"},
        }])
    )
    resp = app_client.get("/api/destinations/search", params={"q": "Bali"})
    assert resp.status_code == 200
    data = resp.json()
    assert data and "Bali" in data[0]["name"]


@respx.mock
def test_destinations_weather(app_client, disable_rate_limit):
    respx.get(f"{settings.OPEN_METEO_BASE}/forecast").mock(
        return_value=Response(200, json={"daily": {
            "time": ["2026-05-01"],
            "temperature_2m_max": [30.0], "temperature_2m_min": [22.0],
            "precipitation_sum": [0.0],
        }})
    )
    resp = app_client.get("/api/destinations/weather", params={"lat": -8.34, "lon": 115.09, "days": 1})
    assert resp.status_code == 200
    assert resp.json()["avg_high_c"] == 30.0


@respx.mock
def test_destinations_currency(app_client, disable_rate_limit):
    respx.get(f"{settings.FRANKFURTER_BASE}/latest").mock(
        return_value=Response(200, json={"date": "2026-04-30", "rates": {"EUR": 92.0}})
    )
    resp = app_client.get("/api/destinations/currency", params={"from": "USD", "to": "EUR", "amount": 100})
    assert resp.status_code == 200
    assert resp.json()["amount"] == 92.0

"""Tests for attractions API."""
from __future__ import annotations

import respx
from httpx import Response

from app.config import settings


def test_categories(app_client, disable_rate_limit):
    resp = app_client.get("/api/attractions/categories")
    assert resp.status_code == 200
    cats = resp.json()
    assert "historic" in cats
    assert "museum" in cats


@respx.mock
def test_search_falls_back_to_overpass_then_mock(app_client, disable_rate_limit):
    respx.post(settings.OVERPASS_BASE).mock(return_value=Response(200, json={"elements": []}))
    resp = app_client.get("/api/attractions/search",
                          params={"lat": 48.85, "lon": 2.35, "radius_m": 1500, "limit": 5})
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] >= 1
    assert body["provider"] in ("mock", "overpass")

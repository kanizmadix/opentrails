"""Tests for Overpass POI service."""
from __future__ import annotations

import pytest
import respx
from httpx import Response

from app.config import settings
from app.services import overpass


@pytest.mark.asyncio
@respx.mock
async def test_query_pois_extracts_named_elements():
    respx.post(settings.OVERPASS_BASE).mock(
        return_value=Response(200, json={
            "elements": [
                {"type": "node", "id": 1, "lat": 48.86, "lon": 2.34,
                 "tags": {"name": "Eiffel Tower", "tourism": "attraction"}},
                {"type": "way", "id": 2, "center": {"lat": 48.85, "lon": 2.33},
                 "tags": {"name": "Louvre", "tourism": "museum"}},
                {"type": "node", "id": 3, "lat": 48.86, "lon": 2.35, "tags": {}},  # no name
            ]
        })
    )
    pois = await overpass.query_pois((48.84, 2.32, 48.87, 2.36), ["tourism"])
    names = [p["name"] for p in pois]
    assert "Eiffel Tower" in names
    assert "Louvre" in names
    assert len(pois) == 2  # unnamed dropped

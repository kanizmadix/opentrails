"""Tests for Nominatim service (mocked HTTP)."""
from __future__ import annotations

import pytest
import respx
from httpx import Response

from app.config import settings
from app.services import nominatim


@pytest.mark.asyncio
@respx.mock
async def test_geocode_returns_places():
    respx.get(f"{settings.NOMINATIM_BASE}/search").mock(
        return_value=Response(200, json=[{
            "display_name": "Paris, France",
            "lat": "48.8566", "lon": "2.3522",
            "osm_id": 7444,
            "address": {"country": "France", "country_code": "fr", "state": "Ile-de-France"},
            "extratags": {"wikidata": "Q90"},
        }])
    )
    places = await nominatim.geocode("Paris")
    assert len(places) == 1
    assert places[0].name.startswith("Paris")
    assert places[0].country == "France"
    assert places[0].country_code == "FR"
    assert places[0].geo.lat == pytest.approx(48.8566)


@pytest.mark.asyncio
@respx.mock
async def test_reverse_returns_place():
    respx.get(f"{settings.NOMINATIM_BASE}/reverse").mock(
        return_value=Response(200, json={
            "display_name": "Tokyo, Japan",
            "lat": "35.68", "lon": "139.76",
            "address": {"country": "Japan", "country_code": "jp"},
        })
    )
    place = await nominatim.reverse(35.68, 139.76)
    assert place is not None
    assert place.country == "Japan"


@pytest.mark.asyncio
@respx.mock
async def test_geocode_one_raises_when_empty():
    respx.get(f"{settings.NOMINATIM_BASE}/search").mock(
        return_value=Response(200, json=[])
    )
    from app.exceptions import NotFoundError
    with pytest.raises(NotFoundError):
        await nominatim.geocode_one("Atlantis")

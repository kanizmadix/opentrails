"""Tests for REST Countries service."""
from __future__ import annotations

import pytest
import respx
from httpx import Response

from app.config import settings
from app.services import rest_countries

_PAYLOAD = {
    "name": {"common": "Japan", "official": "Japan"},
    "cca2": "JP", "cca3": "JPN",
    "capital": ["Tokyo"],
    "region": "Asia", "subregion": "Eastern Asia",
    "population": 125_000_000, "area": 377_975.0,
    "languages": {"jpn": "Japanese"},
    "currencies": {"JPY": {"name": "Japanese yen", "symbol": "¥"}},
    "timezones": ["UTC+09:00"],
    "flag": "🇯🇵",
    "flags": {"svg": "https://flag.svg"},
    "idd": {"root": "+8", "suffixes": ["1"]},
    "car": {"side": "left"},
}


@pytest.mark.asyncio
@respx.mock
async def test_country_by_alpha2():
    respx.get(f"{settings.REST_COUNTRIES_BASE}/alpha/JP").mock(
        return_value=Response(200, json=_PAYLOAD)
    )
    profile = await rest_countries.country("JP")
    assert profile.name == "Japan"
    assert profile.code_alpha2 == "JP"
    assert profile.capital == "Tokyo"
    assert profile.calling_code == "+81"
    assert profile.drives_on == "left"


@pytest.mark.asyncio
@respx.mock
async def test_country_by_name():
    respx.get(f"{settings.REST_COUNTRIES_BASE}/name/Japan").mock(
        return_value=Response(200, json=[_PAYLOAD])
    )
    profile = await rest_countries.country("Japan")
    assert profile.code_alpha3 == "JPN"

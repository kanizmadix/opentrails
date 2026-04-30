"""Tests for Open-Meteo weather service."""
from __future__ import annotations

import pytest
import respx
from httpx import Response

from app.config import settings
from app.services import open_meteo


@pytest.mark.asyncio
@respx.mock
async def test_forecast_summarizes_daily():
    respx.get(f"{settings.OPEN_METEO_BASE}/forecast").mock(
        return_value=Response(200, json={
            "daily": {
                "time": ["2026-05-01", "2026-05-02", "2026-05-03"],
                "temperature_2m_max": [20.0, 22.0, 24.0],
                "temperature_2m_min": [10.0, 12.0, 14.0],
                "precipitation_sum": [0.0, 5.0, 0.5],
            }
        })
    )
    summary = await open_meteo.forecast(48.85, 2.35, days=3)
    assert summary.avg_high_c == pytest.approx(22.0)
    assert summary.avg_low_c == pytest.approx(12.0)
    assert summary.rainy_days == 1
    assert summary.summary
    assert len(summary.daily_high_c) == 3


@pytest.mark.asyncio
@respx.mock
async def test_historical_climate_returns_summary():
    respx.get("https://archive-api.open-meteo.com/v1/archive").mock(
        return_value=Response(200, json={
            "daily": {
                "time": ["2023-01-01"],
                "temperature_2m_max": [5.0],
                "temperature_2m_min": [-2.0],
                "precipitation_sum": [3.0],
            }
        })
    )
    summary = await open_meteo.historical_climate(48.85, 2.35)
    assert summary.avg_high_c == 5.0

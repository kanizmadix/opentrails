"""Tests for Frankfurter currency service."""
from __future__ import annotations

import pytest
import respx
from httpx import Response

from app.config import settings
from app.services import frankfurter


@pytest.mark.asyncio
@respx.mock
async def test_convert_returns_rate():
    respx.get(f"{settings.FRANKFURTER_BASE}/latest").mock(
        return_value=Response(200, json={"date": "2026-04-30", "rates": {"EUR": 92.5}})
    )
    result = await frankfurter.convert("USD", "EUR", amount=100.0)
    assert result["amount"] == 92.5
    assert result["from"] == "USD"
    assert result["to"] == "EUR"
    assert result["rate"] == pytest.approx(0.925)


@pytest.mark.asyncio
async def test_convert_same_currency_short_circuits():
    result = await frankfurter.convert("USD", "USD", amount=50.0)
    assert result["amount"] == 50.0
    assert result["rate"] == 1.0


@pytest.mark.asyncio
@respx.mock
async def test_latest_rates_returns_dict():
    respx.get(f"{settings.FRANKFURTER_BASE}/latest").mock(
        return_value=Response(200, json={"date": "2026-04-30",
                                         "rates": {"EUR": 0.92, "GBP": 0.78}})
    )
    rates = await frankfurter.latest_rates("USD")
    assert rates["EUR"] == 0.92
    assert rates["GBP"] == 0.78

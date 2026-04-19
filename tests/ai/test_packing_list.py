"""Tests for AI packing list generator."""
from __future__ import annotations

import json
from datetime import date

from app.ai import packing_list
from app.models.destinations import CountryProfile, WeatherSummary
from app.models.packing import PackingRequest


def test_generate_packing_parses_response(mock_claude):
    payload = {
        "items": [
            {"name": "T-shirts", "quantity": 5, "category": "clothing",
             "essential": True, "notes": "lightweight"},
            {"name": "Universal adapter", "quantity": 1, "category": "electronics",
             "essential": True, "notes": "Type C plug"},
            {"name": "Passport", "quantity": 1, "category": "documents", "essential": True},
            {"name": "BadCategoryWillFallback", "quantity": 1, "category": "wat", "essential": False},
        ],
        "weight_estimate_kg": 6.5,
        "forgotten_warnings": ["Sunglasses", "Insurance card"],
        "weather_summary": "Warm, breezy.",
    }
    mock_claude.set_response(json.dumps(payload))

    req = PackingRequest(
        destination="Barcelona", start_date=date(2026, 7, 1), end_date=date(2026, 7, 7),
        travelers=2, activities=["beach", "tapas"], luggage_type="carryon",
    )
    weather = WeatherSummary(summary="Avg high 28°C")
    country = CountryProfile(name="Spain", code_alpha2="ES", plug_types=["C", "F"])
    packing = packing_list.generate_packing(req, weather, country)
    assert len(packing.items) == 4
    assert packing.weight_estimate_kg == 6.5
    assert "Sunglasses" in packing.forgotten_warnings
    # invalid category falls back to misc
    assert packing.items[-1].category.value == "misc"

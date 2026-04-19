"""Tests for AI itinerary builder (Claude mocked)."""
from __future__ import annotations

import json
from datetime import date

from app.ai import itinerary_builder
from app.models.attractions import Attraction, AttractionCategory
from app.models.common import GeoPoint
from app.models.destinations import WeatherSummary
from app.models.itinerary import ItineraryRequest


def test_build_itinerary_parses_claude_json(mock_claude):
    payload = {
        "title": "3-Day Lisbon",
        "summary": "A relaxed weekend in Lisbon.",
        "days": [
            {
                "day": 1, "date": "2026-06-01", "title": "Old Town",
                "activities": [
                    {"time_of_day": "morning", "title": "Castelo de São Jorge",
                     "description": "Hilltop fortress views",
                     "category": "historic", "duration_minutes": 120,
                     "cost_estimate": {"amount": 15.0, "currency": "EUR"},
                     "location_name": "Lisbon", "transit_from_previous": "Walk",
                     "booking_required": False},
                ],
                "meal_suggestions": ["Pastéis de Belém"],
                "daily_budget_estimate": {"amount": 120.0, "currency": "EUR"},
                "notes": "Wear comfy shoes.",
            }
        ],
        "budget": {
            "accommodation": {"amount": 200, "currency": "EUR"},
            "food": {"amount": 80, "currency": "EUR"},
            "transport": {"amount": 40, "currency": "EUR"},
            "activities": {"amount": 60, "currency": "EUR"},
            "miscellaneous": {"amount": 20, "currency": "EUR"},
            "total": {"amount": 400, "currency": "EUR"},
        },
        "packing_highlights": ["sunscreen", "walking shoes"],
        "tips": ["Buy a 24h transit pass"],
    }
    mock_claude.set_response(json.dumps(payload))

    req = ItineraryRequest(
        destination="Lisbon", start_date=date(2026, 6, 1), end_date=date(2026, 6, 3),
        travelers=2, budget_usd=500.0,
    )
    weather = WeatherSummary(summary="Mild and sunny")
    attractions = [Attraction(xid="x1", name="Castle",
                              geo=GeoPoint(lat=38.7, lon=-9.1),
                              category=AttractionCategory.HISTORIC)]
    itin = itinerary_builder.build_itinerary(req, attractions, weather)
    assert itin.title == "3-Day Lisbon"
    assert len(itin.days) == 1
    assert itin.budget.total.amount == 400
    assert "sunscreen" in itin.packing_highlights


def test_build_itinerary_handles_minimal_response(mock_claude):
    mock_claude.set_response("{}")
    req = ItineraryRequest(
        destination="Nowhere", start_date=date(2026, 7, 1), end_date=date(2026, 7, 1),
        travelers=1,
    )
    itin = itinerary_builder.build_itinerary(req, [], WeatherSummary())
    assert itin.title.startswith("Trip")
    assert len(itin.days) == 1

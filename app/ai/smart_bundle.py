"""AI-powered 'best bundle' recommender — picks flight + hotel + attractions."""
from __future__ import annotations

from typing import Any, Dict, List

from app.ai.claude_client import claude_call
from app.models.attractions import Attraction
from app.models.flights import FlightOffer
from app.models.hotels import HotelOffer
from app.models.trips import TripRecord

SYSTEM_PROMPT = """You curate optimal travel bundles. Given a trip profile, candidate
flights, candidate hotels, and a list of attractions, you choose:
- ONE flight (best balance of price, duration, time of day)
- ONE hotel (best balance of price, rating, amenities, location)
- 5-7 attractions that fit the budget and pace

You explain your reasoning concisely. Stay within budget when set.

ALWAYS respond with valid JSON only.
"""


def _summarize_flights(flights: List[FlightOffer]) -> str:
    rows = []
    for f in flights[:10]:
        total_min = sum(s.duration_minutes for s in f.segments)
        rows.append(
            f"- id={f.id} provider={f.provider} price={f.price.total.amount:.0f}{f.price.total.currency}"
            f" duration={total_min}min stops={max(0, len(f.segments) - 1)}"
        )
    return "\n".join(rows) or "(no candidates)"


def _summarize_hotels(hotels: List[HotelOffer]) -> str:
    rows = []
    for h in hotels[:10]:
        rows.append(
            f"- id={h.id} {h.name!r} rating={h.star_rating}"
            f" nightly={h.nightly_price.amount:.0f}{h.nightly_price.currency}"
            f" total={h.total_price.amount:.0f}{h.total_price.currency}"
        )
    return "\n".join(rows) or "(no candidates)"


def _summarize_attractions(attractions: List[Attraction]) -> str:
    rows = [f"- xid={a.xid} {a.name} ({a.category.value})" for a in attractions[:25]]
    return "\n".join(rows) or "(no candidates)"


def recommend_bundle(trip: TripRecord, flights: List[FlightOffer],
                     hotels: List[HotelOffer],
                     attractions: List[Attraction]) -> Dict[str, Any]:
    user = f"""TRIP: {trip.name} -> {trip.destination}
DATES: {trip.start_date} to {trip.end_date}
TRAVELERS: {trip.travelers}
BUDGET: {f"${trip.budget_usd} USD" if trip.budget_usd else "flexible"}

FLIGHTS:
{_summarize_flights(flights)}

HOTELS:
{_summarize_hotels(hotels)}

ATTRACTIONS:
{_summarize_attractions(attractions)}

Respond with JSON:
{{
  "flight_id": "...",
  "hotel_id": "...",
  "attraction_xids": ["...", "..."],
  "rationale": "2-3 sentences explaining why",
  "estimated_total_usd": 1234.56,
  "warnings": ["..."]
}}
"""
    data = claude_call(system=SYSTEM_PROMPT, user=user, max_tokens=1024, json_mode=True)
    return {
        "flight_id": data.get("flight_id"),
        "hotel_id": data.get("hotel_id"),
        "attraction_xids": list(data.get("attraction_xids") or []),
        "rationale": data.get("rationale", ""),
        "estimated_total_usd": data.get("estimated_total_usd"),
        "warnings": list(data.get("warnings") or []),
    }

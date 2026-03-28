"""AI-powered itinerary builder using Claude with prompt caching."""
from __future__ import annotations

from datetime import date, timedelta
from typing import List

from app.ai.claude_client import claude_call
from app.logger import get_logger
from app.models.attractions import Attraction
from app.models.common import Money
from app.models.destinations import WeatherSummary
from app.models.itinerary import (
    BudgetBreakdown, DayPlan, ItineraryActivity, ItineraryRequest, ItineraryResponse,
)

log = get_logger(__name__)

SYSTEM_PROMPT = """You are an expert travel planner. You produce day-by-day itineraries that:

- Respect the traveler's pace (relaxed/balanced/packed) and budget
- Group nearby attractions to minimize transit
- Schedule three time-of-day activities per day: morning, afternoon, evening
- Include realistic transit notes between activities
- Suggest local meal options (breakfast, lunch, dinner) reflecting cuisine
- Estimate per-day and overall budget broken down by category
- Surface practical tips and packing highlights tailored to weather and culture

You ALWAYS respond with valid JSON exactly matching the requested schema. No prose, no code fences.
"""


def _format_attractions(attractions: List[Attraction]) -> str:
    if not attractions:
        return "No specific attractions provided — use your knowledge of the destination."
    lines = [
        f"- {a.name} ({a.category.value}) at ({a.geo.lat:.4f}, {a.geo.lon:.4f})"
        for a in attractions[:30]
    ]
    return "\n".join(lines)


def _format_weather(weather: WeatherSummary) -> str:
    if not weather or weather.summary is None:
        return "Weather data unavailable."
    return weather.summary


def _build_user_prompt(req: ItineraryRequest, attractions: List[Attraction],
                       weather: WeatherSummary) -> str:
    duration = (req.end_date - req.start_date).days + 1
    return f"""Plan a {duration}-day trip to {req.destination}.

TRAVELERS: {req.travelers}
DATES: {req.start_date.isoformat()} to {req.end_date.isoformat()}
PACE: {req.pace}
BUDGET: {f"${req.budget_usd} USD total" if req.budget_usd else "flexible"}
INTERESTS: {", ".join(req.interests) or "general sightseeing"}
DIETARY: {", ".join(req.dietary) or "none"}
MOBILITY: {req.mobility or "no restrictions"}
NOTES: {req.notes or "(none)"}

WEATHER FORECAST: {_format_weather(weather)}

CANDIDATE ATTRACTIONS:
{_format_attractions(attractions)}

Respond with this JSON shape:
{{
  "title": "...",
  "summary": "2-3 sentence trip overview",
  "days": [
    {{
      "day": 1,
      "date": "YYYY-MM-DD",
      "title": "...",
      "activities": [
        {{"time_of_day": "morning", "title": "...", "description": "...",
          "category": "...", "duration_minutes": 120,
          "cost_estimate": {{"amount": 25.0, "currency": "USD"}},
          "location_name": "...", "transit_from_previous": "...",
          "booking_required": false}}
      ],
      "meal_suggestions": ["..."],
      "daily_budget_estimate": {{"amount": 150.0, "currency": "USD"}},
      "notes": "..."
    }}
  ],
  "budget": {{
    "accommodation": {{"amount": 0, "currency": "USD"}},
    "food": {{"amount": 0, "currency": "USD"}},
    "transport": {{"amount": 0, "currency": "USD"}},
    "activities": {{"amount": 0, "currency": "USD"}},
    "miscellaneous": {{"amount": 0, "currency": "USD"}},
    "total": {{"amount": 0, "currency": "USD"}}
  }},
  "packing_highlights": ["..."],
  "tips": ["..."]
}}
"""


def build_itinerary(req: ItineraryRequest, attractions: List[Attraction],
                    weather: WeatherSummary) -> ItineraryResponse:
    user_prompt = _build_user_prompt(req, attractions, weather)
    data = claude_call(system=SYSTEM_PROMPT, user=user_prompt,
                       max_tokens=4096, json_mode=True)
    days = [_coerce_day(d, req.start_date, idx) for idx, d in enumerate(data.get("days") or [])]
    if not days:
        # one-day fallback
        days = [DayPlan(day=1, date=req.start_date, title=f"Day in {req.destination}",
                        activities=[])]
    budget = data.get("budget")
    return ItineraryResponse(
        request=req,
        title=data.get("title") or f"Trip to {req.destination}",
        summary=data.get("summary") or "",
        days=days,
        budget=_coerce_budget(budget) if budget else None,
        packing_highlights=list(data.get("packing_highlights") or []),
        tips=list(data.get("tips") or []),
    )


def _coerce_day(d: dict, start_date: date, idx: int) -> DayPlan:
    raw_date = d.get("date")
    try:
        day_date = date.fromisoformat(raw_date) if raw_date else start_date + timedelta(days=idx)
    except (TypeError, ValueError):
        day_date = start_date + timedelta(days=idx)
    activities: List[ItineraryActivity] = []
    for a in d.get("activities") or []:
        try:
            activities.append(ItineraryActivity.model_validate(a))
        except Exception:
            continue
    daily_budget = d.get("daily_budget_estimate")
    return DayPlan(
        day=int(d.get("day") or idx + 1),
        date=day_date,
        title=d.get("title") or f"Day {idx + 1}",
        activities=activities,
        meal_suggestions=list(d.get("meal_suggestions") or []),
        daily_budget_estimate=Money(**daily_budget) if daily_budget else None,
        notes=d.get("notes"),
    )


def _coerce_budget(b: dict) -> BudgetBreakdown:
    def _money(key: str) -> Money:
        v = b.get(key) or {}
        return Money(amount=float(v.get("amount", 0.0)), currency=v.get("currency", "USD"))
    return BudgetBreakdown(
        accommodation=_money("accommodation"),
        food=_money("food"),
        transport=_money("transport"),
        activities=_money("activities"),
        miscellaneous=_money("miscellaneous"),
        total=_money("total"),
    )

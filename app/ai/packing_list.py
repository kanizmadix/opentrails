"""AI-powered packing list generator."""
from __future__ import annotations

from app.ai.claude_client import claude_call
from app.logger import get_logger
from app.models.destinations import CountryProfile, WeatherSummary
from app.models.packing import PackingCategory, PackingItem, PackingList, PackingRequest

log = get_logger(__name__)

SYSTEM_PROMPT = """You are a meticulous travel packing assistant. Given a destination,
travel dates, weather, country profile, and planned activities, you produce a
comprehensive packing list grouped into:
- clothing (weather + activity appropriate)
- electronics (with adapter notes per country plug type)
- documents (passport, visa, insurance, copies)
- toiletries (TSA-friendly when carry-on)
- medical (basic first aid + destination-specific advice)
- activity (gear specific to listed activities)
- misc (snacks, eye mask, etc.)

You are practical, weight-aware, and tailor to luggage type. You include essential flags
and surface "forgotten warnings" — items travelers commonly forget for this profile.

ALWAYS respond with valid JSON only.
"""


def _build_user_prompt(req: PackingRequest, weather: WeatherSummary,
                       country: CountryProfile) -> str:
    nights = (req.end_date - req.start_date).days
    return f"""Build a packing list for this trip:

DESTINATION: {req.destination}
DATES: {req.start_date.isoformat()} to {req.end_date.isoformat()} ({nights} nights)
TRAVELERS: {req.travelers}{" (with kids)" if req.has_kids else ""}
ACTIVITIES: {", ".join(req.activities) or "general sightseeing"}
LUGGAGE: {req.luggage_type}
SEASON HINT: {req.season or "auto-detect"}
NOTES: {req.notes or "(none)"}

WEATHER: {weather.summary or "unknown"}
COUNTRY: {country.name} (plug types: {", ".join(country.plug_types) or "unknown"};
drives on: {country.drives_on or "unknown"}; calling code: {country.calling_code or "unknown"})

Respond with JSON:
{{
  "items": [
    {{"name": "...", "quantity": 1, "category": "clothing|electronics|documents|toiletries|medical|activity|misc",
      "essential": true, "notes": "..."}}
  ],
  "weight_estimate_kg": 8.5,
  "forgotten_warnings": ["..."],
  "weather_summary": "short paragraph"
}}
"""


def generate_packing(req: PackingRequest, weather: WeatherSummary,
                     country: CountryProfile) -> PackingList:
    user_prompt = _build_user_prompt(req, weather, country)
    data = claude_call(system=SYSTEM_PROMPT, user=user_prompt,
                       max_tokens=2048, json_mode=True)
    items = []
    for raw in data.get("items") or []:
        try:
            cat = raw.get("category", "misc")
            items.append(PackingItem(
                name=raw.get("name", "item"),
                quantity=int(raw.get("quantity", 1)),
                category=PackingCategory(cat) if cat in {c.value for c in PackingCategory}
                else PackingCategory.MISC,
                essential=bool(raw.get("essential", False)),
                notes=raw.get("notes"),
            ))
        except Exception:
            continue
    return PackingList(
        request=req,
        items=items,
        weight_estimate_kg=data.get("weight_estimate_kg"),
        forgotten_warnings=list(data.get("forgotten_warnings") or []),
        weather_summary=data.get("weather_summary"),
    )

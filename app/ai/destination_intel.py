"""AI synthesis of destination intelligence (safety, etiquette, scams, visa)."""
from __future__ import annotations

from typing import Any, Dict

from app.ai.claude_client import claude_call
from app.models.destinations import (
    BestSeasonInfo, CountryProfile, DestinationIntel, VisaInfo, WeatherSummary,
)

SYSTEM_PROMPT = """You are a seasoned travel advisor. Given a country profile, weather data,
and Wikivoyage extracts, you synthesize practical destination intelligence:
- Visa requirements (best-effort, label as "indicative — verify with embassy")
- Best season to visit + months to avoid (with climate reasoning)
- Top 5-7 safety tips
- Cultural etiquette do's and don'ts (5+)
- Common scams to avoid (3-5)
- Tipping norms summary
- Emergency numbers (police, ambulance, fire) when known
- Plug type warning + voltage if relevant
- 3-4 sentence overview summary

ALWAYS respond with valid JSON only. Be honest about uncertainty.
"""


def _user_prompt(country: CountryProfile, wikivoyage: Dict[str, Any],
                 weather: WeatherSummary) -> str:
    wv_extract = (wikivoyage or {}).get("extract") or "(no Wikivoyage data)"
    return f"""Compile destination intel for {country.name}.

COUNTRY PROFILE:
- Capital: {country.capital}
- Region: {country.region} / {country.subregion}
- Languages: {", ".join(country.languages.values()) or "unknown"}
- Currencies: {", ".join(country.currencies.keys()) or "unknown"}
- Calling code: {country.calling_code}
- Drives on: {country.drives_on}

WEATHER (forecast/normals): {weather.summary or "unknown"}

WIKIVOYAGE EXTRACT (truncated):
{wv_extract[:1500]}

Respond with JSON:
{{
  "visa": {{"requirement": "visa-free|visa-on-arrival|e-visa|required|unknown",
            "max_stay_days": 30, "notes": "...", "source": "indicative"}},
  "best_season": {{"best_months": ["Mar","Apr"], "avoid_months": ["Jul"], "reason": "..."}},
  "safety_tips": ["..."],
  "cultural_etiquette": ["..."],
  "common_scams": ["..."],
  "tipping_norms": "...",
  "emergency_numbers": {{"police": "...", "ambulance": "...", "fire": "..."}},
  "summary": "...",
  "plug_types": ["A", "B"]
}}
"""


def compile_intel(country: CountryProfile, wikivoyage: Dict[str, Any],
                  weather: WeatherSummary) -> DestinationIntel:
    data = claude_call(system=SYSTEM_PROMPT,
                       user=_user_prompt(country, wikivoyage, weather),
                       max_tokens=2048, json_mode=True)
    plug_types = list(data.get("plug_types") or [])
    if plug_types and not country.plug_types:
        country = country.model_copy(update={"plug_types": plug_types})
    visa_raw = data.get("visa") or {}
    visa = VisaInfo(
        requirement=visa_raw.get("requirement", "unknown"),
        max_stay_days=visa_raw.get("max_stay_days"),
        notes=visa_raw.get("notes"),
        source=visa_raw.get("source") or "indicative — verify with embassy",
    ) if visa_raw else None
    bs_raw = data.get("best_season") or {}
    best_season = BestSeasonInfo(
        best_months=list(bs_raw.get("best_months") or []),
        avoid_months=list(bs_raw.get("avoid_months") or []),
        reason=bs_raw.get("reason"),
    ) if bs_raw else None
    return DestinationIntel(
        country=country,
        visa=visa,
        weather=weather,
        best_season=best_season,
        safety_tips=list(data.get("safety_tips") or []),
        cultural_etiquette=list(data.get("cultural_etiquette") or []),
        common_scams=list(data.get("common_scams") or []),
        tipping_norms=data.get("tipping_norms"),
        emergency_numbers=dict(data.get("emergency_numbers") or {}),
        summary=data.get("summary"),
        wikivoyage_url=(wikivoyage or {}).get("url"),
    )

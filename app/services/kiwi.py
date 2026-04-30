"""Kiwi.com Tequila API client (flight search, requires API key)."""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, List

from app.config import settings
from app.exceptions import ConfigurationError
from app.logger import get_logger
from app.models.common import Money
from app.models.flights import FlightOffer, FlightPrice, FlightSegment
from app.utils.http import get_json

log = get_logger(__name__)


def _ensure_key() -> None:
    if not settings.KIWI_API_KEY:
        raise ConfigurationError("Kiwi API key not configured (set KIWI_API_KEY)")


async def flight_search(*, origin: str, destination: str, date_from: date,
                        date_to: date | None = None, adults: int = 1,
                        currency: str = "USD", limit: int = 20) -> List[FlightOffer]:
    _ensure_key()
    date_to = date_to or date_from + timedelta(days=1)
    params = {
        "fly_from": origin.upper(),
        "fly_to": destination.upper(),
        "date_from": date_from.strftime("%d/%m/%Y"),
        "date_to": date_to.strftime("%d/%m/%Y"),
        "adults": adults,
        "curr": currency,
        "limit": limit,
        "sort": "price",
    }
    url = f"{settings.KIWI_BASE}/v2/search"
    raw = await get_json(url, params=params, headers={"apikey": settings.KIWI_API_KEY})
    return [_to_offer(item, currency) for item in (raw.get("data") or [])]


def _to_offer(item: Dict[str, Any], currency: str) -> FlightOffer:
    segments: List[FlightSegment] = []
    for route in item.get("route", []):
        segments.append(FlightSegment(
            origin=route.get("flyFrom", ""),
            destination=route.get("flyTo", ""),
            departure_at=datetime.fromisoformat(route.get("local_departure", "").replace("Z", "+00:00"))
            if route.get("local_departure") else datetime.utcnow(),
            arrival_at=datetime.fromisoformat(route.get("local_arrival", "").replace("Z", "+00:00"))
            if route.get("local_arrival") else datetime.utcnow(),
            carrier=route.get("airline", ""),
            flight_number=f"{route.get('airline','')}{route.get('flight_no','')}",
            duration_minutes=int((route.get("duration") or 0) / 60) if route.get("duration") else 0,
        ))
    price = float(item.get("price", 0.0))
    return FlightOffer(
        id=str(item.get("id", "")),
        provider="kiwi",
        segments=segments,
        price=FlightPrice(total=Money(amount=price, currency=currency)),
        booking_url=item.get("deep_link"),
        baggage_included=bool(item.get("bags_price", {}).get("1")),
    )

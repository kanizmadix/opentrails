"""Amadeus Self-Service API client (flight + hotel offers)."""
from __future__ import annotations

import time
from datetime import date, datetime
from typing import Any

import httpx

from app.config import settings
from app.exceptions import ConfigurationError, UpstreamAPIError
from app.logger import get_logger
from app.models.common import GeoPoint, Money
from app.models.flights import (
    FlightOffer,
    FlightPrice,
    FlightSegment,
)
from app.models.hotels import HotelAmenities, HotelOffer
from app.utils.http import get_json

log = get_logger(__name__)

_token_cache: dict[str, Any] = {"token": None, "expires_at": 0.0}


def _ensure_keys() -> None:
    if not (settings.AMADEUS_CLIENT_ID and settings.AMADEUS_CLIENT_SECRET):
        raise ConfigurationError("Amadeus credentials not configured (set AMADEUS_CLIENT_ID/SECRET)")


async def get_token() -> str:
    _ensure_keys()
    if _token_cache["token"] and _token_cache["expires_at"] > time.time() + 30:
        return _token_cache["token"]
    url = f"{settings.AMADEUS_BASE}/v1/security/oauth2/token"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.post(url, data={
                "grant_type": "client_credentials",
                "client_id": settings.AMADEUS_CLIENT_ID,
                "client_secret": settings.AMADEUS_CLIENT_SECRET,
            }, headers={"Content-Type": "application/x-www-form-urlencoded"})
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise UpstreamAPIError(f"Amadeus auth failed: {exc}") from exc
    data = resp.json()
    _token_cache["token"] = data["access_token"]
    _token_cache["expires_at"] = time.time() + int(data.get("expires_in", 1500))
    return _token_cache["token"]


async def _auth_get(path: str, params: dict[str, Any]) -> dict[str, Any]:
    token = await get_token()
    url = f"{settings.AMADEUS_BASE}{path}"
    return await get_json(url, params=params, headers={"Authorization": f"Bearer {token}"})


async def flight_offers(*, origin: str, destination: str, departure_date: date,
                        return_date: date | None = None, adults: int = 1,
                        currency: str = "USD", max_results: int = 20) -> list[FlightOffer]:
    """Search Amadeus flight offers."""
    _ensure_keys()
    params: dict[str, Any] = {
        "originLocationCode": origin.upper(),
        "destinationLocationCode": destination.upper(),
        "departureDate": departure_date.isoformat(),
        "adults": adults,
        "currencyCode": currency,
        "max": max_results,
    }
    if return_date:
        params["returnDate"] = return_date.isoformat()
    raw = await _auth_get("/v2/shopping/flight-offers", params)
    return [_to_flight_offer(o) for o in (raw.get("data") or [])]


def _to_flight_offer(offer: dict[str, Any]) -> FlightOffer:
    segments: list[FlightSegment] = []
    for itin in offer.get("itineraries", []):
        for seg in itin.get("segments", []):
            duration_str = seg.get("duration") or "PT0M"
            duration_min = _iso8601_duration_to_minutes(duration_str)
            segments.append(FlightSegment(
                origin=seg["departure"]["iataCode"],
                destination=seg["arrival"]["iataCode"],
                departure_at=datetime.fromisoformat(seg["departure"]["at"]),
                arrival_at=datetime.fromisoformat(seg["arrival"]["at"]),
                carrier=seg.get("carrierCode", ""),
                flight_number=f"{seg.get('carrierCode','')}{seg.get('number','')}",
                duration_minutes=duration_min,
                cabin=(offer.get("travelerPricings", [{}])[0]
                       .get("fareDetailsBySegment", [{}])[0].get("cabin", "ECONOMY")),
            ))
    price = offer.get("price", {})
    total = Money(amount=float(price.get("total", 0.0)), currency=price.get("currency", "USD"))
    base = Money(amount=float(price.get("base", 0.0)),
                 currency=price.get("currency", "USD")) if price.get("base") else None
    return FlightOffer(
        id=offer.get("id", ""),
        provider="amadeus",
        segments=segments,
        price=FlightPrice(total=total, base=base),
        seats_available=offer.get("numberOfBookableSeats"),
        refundable=not offer.get("nonRefundable", True),
    )


def _iso8601_duration_to_minutes(s: str) -> int:
    # e.g. "PT2H30M"
    s = s.replace("PT", "")
    hours = 0
    minutes = 0
    if "H" in s:
        h, _, s = s.partition("H")
        hours = int(h or 0)
    if "M" in s:
        m, _, _ = s.partition("M")
        minutes = int(m or 0)
    return hours * 60 + minutes


async def hotel_offers(*, city_code: str, check_in: date, check_out: date,
                       adults: int = 2) -> list[HotelOffer]:
    """Search Amadeus hotel offers (city-search + offers)."""
    _ensure_keys()
    list_params = {"cityCode": city_code.upper(), "radius": 20, "radiusUnit": "KM"}
    list_resp = await _auth_get("/v1/reference-data/locations/hotels/by-city", list_params)
    hotel_ids = [h["hotelId"] for h in (list_resp.get("data") or [])[:30]]
    if not hotel_ids:
        return []
    offers_params = {
        "hotelIds": ",".join(hotel_ids),
        "checkInDate": check_in.isoformat(),
        "checkOutDate": check_out.isoformat(),
        "adults": adults,
    }
    raw = await _auth_get("/v3/shopping/hotel-offers", offers_params)
    return [_to_hotel_offer(item) for item in (raw.get("data") or []) if item.get("offers")]


def _to_hotel_offer(item: dict[str, Any]) -> HotelOffer:
    h = item.get("hotel", {})
    offers = item.get("offers", [])
    cheapest = min(offers, key=lambda o: float(o.get("price", {}).get("total", 1e9)))
    price = cheapest.get("price", {})
    total_amount = float(price.get("total", 0.0))
    nights = max((cheapest.get("checkOutDate", "") and cheapest.get("checkInDate", "") and 1) or 1, 1)
    geo: GeoPoint | None = None
    if h.get("latitude") is not None and h.get("longitude") is not None:
        geo = GeoPoint(lat=float(h["latitude"]), lon=float(h["longitude"]))
    return HotelOffer(
        id=h.get("hotelId", ""),
        provider="amadeus",
        name=h.get("name", ""),
        address=", ".join(filter(None, (h.get("address") or {}).get("lines", []))) or None,
        geo=geo,
        star_rating=float(h["rating"]) if h.get("rating") else None,
        amenities=HotelAmenities(),
        nightly_price=Money(amount=total_amount / nights,
                            currency=price.get("currency", "USD")),
        total_price=Money(amount=total_amount, currency=price.get("currency", "USD")),
        cancellation_policy=(cheapest.get("policies") or {}).get("cancellation", {}).get("description", {}).get("text"),
    )

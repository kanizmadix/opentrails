"""Provider router: picks Amadeus / Kiwi / OpenTripMap / Overpass with fallbacks.

If no providers are configured, returns clearly-tagged mock data so the UI
remains usable in dev mode.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import List

from app.config import settings
from app.logger import get_logger
from app.models.attractions import Attraction, AttractionCategory
from app.models.common import GeoPoint, Money
from app.models.flights import (
    FlightOffer, FlightPrice, FlightSearchRequest, FlightSearchResponse, FlightSegment,
)
from app.models.hotels import HotelAmenities, HotelOffer, HotelSearchRequest, HotelSearchResponse
from app.services import amadeus, kiwi, opentripmap

log = get_logger(__name__)


# ---------------- flights ---------------- #


def _has_amadeus() -> bool:
    return bool(settings.AMADEUS_CLIENT_ID and settings.AMADEUS_CLIENT_SECRET)


def _has_kiwi() -> bool:
    return bool(settings.KIWI_API_KEY)


async def search_flights(req: FlightSearchRequest) -> FlightSearchResponse:
    provider = "mock"
    offers: List[FlightOffer] = []
    if _has_amadeus():
        provider = "amadeus"
        try:
            offers = await amadeus.flight_offers(
                origin=req.origin, destination=req.destination,
                departure_date=req.departure_date, return_date=req.return_date,
                adults=req.adults, currency=req.currency, max_results=req.max_results,
            )
        except Exception as exc:
            log.warning("amadeus_flights_failed", err=str(exc))
            offers = []
    if not offers and _has_kiwi():
        provider = "kiwi"
        try:
            offers = await kiwi.flight_search(
                origin=req.origin, destination=req.destination,
                date_from=req.departure_date, date_to=req.return_date,
                adults=req.adults, currency=req.currency, limit=req.max_results,
            )
        except Exception as exc:
            log.warning("kiwi_flights_failed", err=str(exc))
            offers = []
    if not offers:
        offers = _mock_flights(req)
        provider = "mock"
    cheapest = min(offers, key=lambda o: o.price.total.amount) if offers else None
    fastest = min(offers,
                  key=lambda o: sum(s.duration_minutes for s in o.segments)) if offers else None
    return FlightSearchResponse(
        request=req, offers=offers, provider=provider,
        fetched_at=datetime.utcnow(), cheapest=cheapest, fastest=fastest,
    )


def _mock_flights(req: FlightSearchRequest) -> List[FlightOffer]:
    base = datetime.combine(req.departure_date, datetime.min.time()).replace(hour=8)
    return [
        FlightOffer(
            id=f"mock-{i}",
            provider="mock",
            segments=[FlightSegment(
                origin=req.origin.upper(), destination=req.destination.upper(),
                departure_at=base + timedelta(hours=i * 3),
                arrival_at=base + timedelta(hours=i * 3 + 4 + i),
                carrier="MK", flight_number=f"MK{100 + i}",
                duration_minutes=240 + i * 30,
            )],
            price=FlightPrice(total=Money(amount=200.0 + i * 75, currency=req.currency)),
        )
        for i in range(min(5, req.max_results))
    ]


# ---------------- hotels ---------------- #


async def search_hotels(req: HotelSearchRequest) -> HotelSearchResponse:
    provider = "mock"
    offers: List[HotelOffer] = []
    if _has_amadeus():
        provider = "amadeus"
        try:
            offers = await amadeus.hotel_offers(
                city_code=req.city, check_in=req.check_in,
                check_out=req.check_out, adults=req.adults,
            )
        except Exception as exc:
            log.warning("amadeus_hotels_failed", err=str(exc))
            offers = []
    if not offers:
        offers = _mock_hotels(req)
        provider = "mock"
    return HotelSearchResponse(
        request=req, offers=offers, provider=provider, fetched_at=datetime.utcnow(),
    )


def _mock_hotels(req: HotelSearchRequest) -> List[HotelOffer]:
    nights = max((req.check_out - req.check_in).days, 1)
    return [
        HotelOffer(
            id=f"mock-hotel-{i}",
            provider="mock",
            name=f"Mock Hotel {i + 1} — {req.city}",
            star_rating=3.0 + (i % 3),
            amenities=HotelAmenities(wifi=True, breakfast=i % 2 == 0, pool=i == 1),
            nightly_price=Money(amount=80.0 + i * 40, currency=req.currency),
            total_price=Money(amount=(80.0 + i * 40) * nights, currency=req.currency),
        )
        for i in range(min(5, req.max_results))
    ]


# ---------------- attractions ---------------- #


async def search_attractions(*, lat: float, lon: float, radius_m: int = 2000,
                             kinds: List[str] | None = None,
                             limit: int = 30) -> tuple[List[Attraction], str]:
    """Returns (attractions, provider). OpenTripMap if keyed, else Overpass."""
    items = await opentripmap.pois_radius(lat, lon, radius_m=radius_m, kinds=kinds, limit=limit)
    provider = "opentripmap" if settings.OPENTRIPMAP_API_KEY else "overpass"
    if not items:
        items = _mock_attractions(lat, lon, limit)
        provider = "mock"
    return items, provider


def _mock_attractions(lat: float, lon: float, limit: int) -> List[Attraction]:
    return [
        Attraction(
            xid=f"mock:{i}",
            name=f"Mock Attraction {i + 1}",
            geo=GeoPoint(lat=lat + i * 0.001, lon=lon + i * 0.001),
            category=AttractionCategory.OTHER,
            distance_m=float(i * 100),
        )
        for i in range(min(5, limit))
    ]

"""Flight search API."""
from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, Query

from app.models.common import Money
from app.models.flights import (
    FareCalendarPoint,
    FlightSearchRequest,
    FlightSearchResponse,
)
from app.services import providers
from app.storage import search_history

PREFIX = "/api/flights"
TAGS = ["flights"]
router = APIRouter()


@router.post("/search", response_model=FlightSearchResponse)
async def search(req: FlightSearchRequest) -> FlightSearchResponse:
    resp = await providers.search_flights(req)
    search_history.log_search("flights", req.model_dump(mode="json"),
                              result_count=len(resp.offers))
    return resp


@router.get("/fare-calendar", response_model=list[FareCalendarPoint])
async def fare_calendar(origin: str = Query(...), destination: str = Query(...),
                        start_date: date = Query(...),
                        days: int = Query(7, ge=1, le=30),
                        currency: str = "USD") -> list[FareCalendarPoint]:
    """Probe fare across consecutive departure dates (one-way)."""
    points: list[FareCalendarPoint] = []
    for offset in range(days):
        d = start_date + timedelta(days=offset)
        try:
            resp = await providers.search_flights(FlightSearchRequest(
                origin=origin, destination=destination, departure_date=d,
                adults=1, currency=currency, max_results=3,
            ))
        except Exception:
            continue
        if not resp.offers:
            continue
        cheapest = min(resp.offers, key=lambda o: o.price.total.amount)
        points.append(FareCalendarPoint(
            departure_date=d,
            price=Money(amount=cheapest.price.total.amount,
                        currency=cheapest.price.total.currency),
            provider=resp.provider,
        ))
    return points

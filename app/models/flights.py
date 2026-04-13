"""Flight search domain models."""
from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.common import Money


class FlightSearchRequest(BaseModel):
    origin: str = Field(..., description="IATA code or city name")
    destination: str = Field(..., description="IATA code or city name")
    departure_date: date
    return_date: date | None = None
    adults: int = Field(1, ge=1, le=9)
    children: int = Field(0, ge=0, le=8)
    cabin: str = Field("ECONOMY")
    currency: str = Field("USD", min_length=3, max_length=3)
    max_results: int = Field(20, ge=1, le=100)
    nonstop_only: bool = False


class FlightSegment(BaseModel):
    origin: str
    destination: str
    departure_at: datetime
    arrival_at: datetime
    carrier: str
    flight_number: str
    duration_minutes: int
    cabin: str = "ECONOMY"


class FlightPrice(BaseModel):
    total: Money
    base: Money | None = None
    taxes: Money | None = None
    per_adult: Money | None = None


class FlightOffer(BaseModel):
    id: str
    provider: str
    segments: list[FlightSegment]
    price: FlightPrice
    seats_available: int | None = None
    booking_url: str | None = None
    refundable: bool | None = None
    baggage_included: bool | None = None


class FlightSearchResponse(BaseModel):
    request: FlightSearchRequest
    offers: list[FlightOffer]
    provider: str
    fetched_at: datetime
    cheapest: FlightOffer | None = None
    fastest: FlightOffer | None = None


class FareCalendarPoint(BaseModel):
    departure_date: date
    price: Money
    provider: str

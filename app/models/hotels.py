"""Hotel search domain models."""
from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.common import GeoPoint, Money


class HotelSearchRequest(BaseModel):
    city: str = Field(..., description="City name or IATA city code")
    check_in: date
    check_out: date
    adults: int = Field(2, ge=1, le=8)
    rooms: int = Field(1, ge=1, le=4)
    currency: str = Field("USD", min_length=3, max_length=3)
    min_rating: Optional[float] = Field(None, ge=0, le=5)
    max_price_per_night: Optional[float] = None
    amenities: List[str] = Field(default_factory=list)
    max_results: int = Field(20, ge=1, le=100)


class HotelAmenities(BaseModel):
    wifi: bool = False
    breakfast: bool = False
    parking: bool = False
    pool: bool = False
    gym: bool = False
    spa: bool = False
    pet_friendly: bool = False
    airport_shuttle: bool = False
    air_conditioning: bool = False
    bar: bool = False
    restaurant: bool = False
    family_friendly: bool = False


class HotelReviewSummary(BaseModel):
    score: Optional[float] = Field(None, ge=0, le=10)
    count: Optional[int] = None
    source: Optional[str] = None
    cleanliness: Optional[float] = None
    location: Optional[float] = None
    value: Optional[float] = None


class HotelOffer(BaseModel):
    id: str
    provider: str
    name: str
    address: Optional[str] = None
    geo: Optional[GeoPoint] = None
    star_rating: Optional[float] = None
    review: Optional[HotelReviewSummary] = None
    amenities: HotelAmenities = Field(default_factory=HotelAmenities)
    photo_url: Optional[str] = None
    nightly_price: Money
    total_price: Money
    booking_url: Optional[str] = None
    cancellation_policy: Optional[str] = None
    distance_to_center_km: Optional[float] = None


class HotelSearchResponse(BaseModel):
    request: HotelSearchRequest
    offers: List[HotelOffer]
    provider: str
    fetched_at: datetime

"""Attraction / point-of-interest models."""
from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from app.models.common import GeoPoint


class AttractionCategory(StrEnum):
    HISTORIC = "historic"
    MUSEUM = "museum"
    NATURE = "nature"
    BEACH = "beach"
    RELIGIOUS = "religious"
    ENTERTAINMENT = "entertainment"
    SHOPPING = "shopping"
    FOOD = "food"
    NIGHTLIFE = "nightlife"
    ARCHITECTURE = "architecture"
    PARK = "park"
    VIEWPOINT = "viewpoint"
    OTHER = "other"


class AttractionSearchRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    radius_m: int = Field(2000, ge=100, le=50000)
    kinds: list[AttractionCategory] = Field(default_factory=list)
    min_rate: int = Field(0, ge=0, le=3, description="OpenTripMap rate filter")
    limit: int = Field(30, ge=1, le=200)


class Attraction(BaseModel):
    xid: str = Field(..., description="Stable identifier (e.g. OSM/OpenTripMap xid)")
    name: str
    geo: GeoPoint
    category: AttractionCategory = AttractionCategory.OTHER
    rate: int | None = None
    distance_m: float | None = None
    wikidata_id: str | None = None
    osm_id: str | None = None
    kinds: list[str] = Field(default_factory=list)


class AttractionDetail(Attraction):
    description: str | None = None
    image_url: str | None = None
    wikipedia_url: str | None = None
    address: str | None = None
    opening_hours: str | None = None
    website: str | None = None


class AttractionsResponse(BaseModel):
    request: AttractionSearchRequest
    items: list[Attraction]
    provider: str
    count: int

"""Attraction / point-of-interest models."""
from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.common import GeoPoint


class AttractionCategory(str, Enum):
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
    kinds: List[AttractionCategory] = Field(default_factory=list)
    min_rate: int = Field(0, ge=0, le=3, description="OpenTripMap rate filter")
    limit: int = Field(30, ge=1, le=200)


class Attraction(BaseModel):
    xid: str = Field(..., description="Stable identifier (e.g. OSM/OpenTripMap xid)")
    name: str
    geo: GeoPoint
    category: AttractionCategory = AttractionCategory.OTHER
    rate: Optional[int] = None
    distance_m: Optional[float] = None
    wikidata_id: Optional[str] = None
    osm_id: Optional[str] = None
    kinds: List[str] = Field(default_factory=list)


class AttractionDetail(Attraction):
    description: Optional[str] = None
    image_url: Optional[str] = None
    wikipedia_url: Optional[str] = None
    address: Optional[str] = None
    opening_hours: Optional[str] = None
    website: Optional[str] = None


class AttractionsResponse(BaseModel):
    request: AttractionSearchRequest
    items: List[Attraction]
    provider: str
    count: int

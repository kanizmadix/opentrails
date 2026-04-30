"""Shared Pydantic models used across domains."""
from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class GeoPoint(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)


class Place(BaseModel):
    name: str
    country: Optional[str] = None
    country_code: Optional[str] = None
    region: Optional[str] = None
    geo: Optional[GeoPoint] = None
    osm_id: Optional[int] = None
    wikidata_id: Optional[str] = None


class Money(BaseModel):
    amount: float
    currency: str = "USD"


class DateRange(BaseModel):
    start: date
    end: date


class HealthResponse(BaseModel):
    status: str = "ok"
    name: str
    version: str
    db: str
    claude_configured: bool

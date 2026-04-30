"""Shared Pydantic models used across domains."""
from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class GeoPoint(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)


class Place(BaseModel):
    name: str
    country: str | None = None
    country_code: str | None = None
    region: str | None = None
    geo: GeoPoint | None = None
    osm_id: int | None = None
    wikidata_id: str | None = None


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

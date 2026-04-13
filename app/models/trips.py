"""Trip, wishlist, and search history persistence models."""
from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


class TripCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    origin: str | None = None
    destination: str
    start_date: date | None = None
    end_date: date | None = None
    travelers: int = Field(1, ge=1, le=20)
    budget_usd: float | None = Field(None, ge=0)
    notes: str | None = None


class TripUpdate(BaseModel):
    name: str | None = None
    origin: str | None = None
    destination: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    travelers: int | None = Field(None, ge=1, le=20)
    budget_usd: float | None = Field(None, ge=0)
    notes: str | None = None


class TripRecord(BaseModel):
    id: int
    name: str
    origin: str | None = None
    destination: str
    start_date: date | None = None
    end_date: date | None = None
    travelers: int = 1
    budget_usd: float | None = None
    notes: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class WishlistItem(BaseModel):
    id: int | None = None
    kind: str = Field(..., description="destination | flight | hotel | attraction")
    payload: dict[str, Any]
    notes: str | None = None
    created_at: datetime | None = None


class SearchHistoryItem(BaseModel):
    id: int | None = None
    domain: str
    query: dict[str, Any]
    result_count: int | None = None
    duration_ms: int | None = None
    created_at: datetime | None = None

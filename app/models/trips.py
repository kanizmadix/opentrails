"""Trip, wishlist, and search history persistence models."""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class TripCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    origin: Optional[str] = None
    destination: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    travelers: int = Field(1, ge=1, le=20)
    budget_usd: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None


class TripUpdate(BaseModel):
    name: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    travelers: Optional[int] = Field(None, ge=1, le=20)
    budget_usd: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None


class TripRecord(BaseModel):
    id: int
    name: str
    origin: Optional[str] = None
    destination: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    travelers: int = 1
    budget_usd: Optional[float] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class WishlistItem(BaseModel):
    id: Optional[int] = None
    kind: str = Field(..., description="destination | flight | hotel | attraction")
    payload: Dict[str, Any]
    notes: Optional[str] = None
    created_at: Optional[datetime] = None


class SearchHistoryItem(BaseModel):
    id: Optional[int] = None
    domain: str
    query: Dict[str, Any]
    result_count: Optional[int] = None
    duration_ms: Optional[int] = None
    created_at: Optional[datetime] = None

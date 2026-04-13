"""Packing list models."""
from __future__ import annotations

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field


class PackingCategory(StrEnum):
    CLOTHING = "clothing"
    ELECTRONICS = "electronics"
    DOCUMENTS = "documents"
    TOILETRIES = "toiletries"
    MEDICAL = "medical"
    ACTIVITY = "activity"
    MISC = "misc"


class PackingRequest(BaseModel):
    destination: str
    start_date: date
    end_date: date
    travelers: int = Field(1, ge=1, le=12)
    activities: list[str] = Field(default_factory=list)
    season: str | None = None
    luggage_type: str = Field("checked", description="carryon | checked | backpack")
    has_kids: bool = False
    notes: str | None = None


class PackingItem(BaseModel):
    name: str
    quantity: int = 1
    category: PackingCategory
    essential: bool = False
    notes: str | None = None


class PackingList(BaseModel):
    request: PackingRequest
    items: list[PackingItem]
    weight_estimate_kg: float | None = None
    forgotten_warnings: list[str] = Field(default_factory=list)
    weather_summary: str | None = None
    generated_by: str = "claude-sonnet-4-6"

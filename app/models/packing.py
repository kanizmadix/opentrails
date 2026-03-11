"""Packing list models."""
from __future__ import annotations

from datetime import date
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class PackingCategory(str, Enum):
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
    activities: List[str] = Field(default_factory=list)
    season: Optional[str] = None
    luggage_type: str = Field("checked", description="carryon | checked | backpack")
    has_kids: bool = False
    notes: Optional[str] = None


class PackingItem(BaseModel):
    name: str
    quantity: int = 1
    category: PackingCategory
    essential: bool = False
    notes: Optional[str] = None


class PackingList(BaseModel):
    request: PackingRequest
    items: List[PackingItem]
    weight_estimate_kg: Optional[float] = None
    forgotten_warnings: List[str] = Field(default_factory=list)
    weather_summary: Optional[str] = None
    generated_by: str = "claude-sonnet-4-6"

"""Itinerary planner models."""
from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.common import Money


class ItineraryRequest(BaseModel):
    destination: str
    start_date: date
    end_date: date
    travelers: int = Field(1, ge=1, le=12)
    budget_usd: Optional[float] = Field(None, ge=0)
    interests: List[str] = Field(default_factory=list)
    pace: str = Field("balanced", description="relaxed | balanced | packed")
    dietary: List[str] = Field(default_factory=list)
    mobility: Optional[str] = None
    notes: Optional[str] = None


class ItineraryActivity(BaseModel):
    time_of_day: str = Field(..., description="morning | afternoon | evening")
    title: str
    description: str
    category: str
    duration_minutes: Optional[int] = None
    cost_estimate: Optional[Money] = None
    location_name: Optional[str] = None
    transit_from_previous: Optional[str] = None
    booking_required: bool = False


class DayPlan(BaseModel):
    day: int
    date: date
    title: str
    activities: List[ItineraryActivity]
    meal_suggestions: List[str] = Field(default_factory=list)
    daily_budget_estimate: Optional[Money] = None
    notes: Optional[str] = None


class BudgetBreakdown(BaseModel):
    accommodation: Money
    food: Money
    transport: Money
    activities: Money
    miscellaneous: Money
    total: Money


class ItineraryResponse(BaseModel):
    request: ItineraryRequest
    title: str
    summary: str
    days: List[DayPlan]
    budget: Optional[BudgetBreakdown] = None
    packing_highlights: List[str] = Field(default_factory=list)
    tips: List[str] = Field(default_factory=list)
    generated_by: str = "claude-sonnet-4-6"

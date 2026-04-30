"""Itinerary planner models."""
from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from app.models.common import Money


class ItineraryRequest(BaseModel):
    destination: str
    start_date: date
    end_date: date
    travelers: int = Field(1, ge=1, le=12)
    budget_usd: float | None = Field(None, ge=0)
    interests: list[str] = Field(default_factory=list)
    pace: str = Field("balanced", description="relaxed | balanced | packed")
    dietary: list[str] = Field(default_factory=list)
    mobility: str | None = None
    notes: str | None = None


class ItineraryActivity(BaseModel):
    time_of_day: str = Field(..., description="morning | afternoon | evening")
    title: str
    description: str
    category: str
    duration_minutes: int | None = None
    cost_estimate: Money | None = None
    location_name: str | None = None
    transit_from_previous: str | None = None
    booking_required: bool = False


class DayPlan(BaseModel):
    day: int
    date: date
    title: str
    activities: list[ItineraryActivity]
    meal_suggestions: list[str] = Field(default_factory=list)
    daily_budget_estimate: Money | None = None
    notes: str | None = None


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
    days: list[DayPlan]
    budget: BudgetBreakdown | None = None
    packing_highlights: list[str] = Field(default_factory=list)
    tips: list[str] = Field(default_factory=list)
    generated_by: str = "claude-sonnet-4-6"

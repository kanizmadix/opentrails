"""Destination intelligence and country profile models."""
from __future__ import annotations

from pydantic import BaseModel, Field


class VisaInfo(BaseModel):
    requirement: str = Field(..., description="visa-free / visa-on-arrival / e-visa / required / unknown")
    max_stay_days: int | None = None
    notes: str | None = None
    source: str | None = None


class WeatherSummary(BaseModel):
    daily_high_c: list[float] = Field(default_factory=list)
    daily_low_c: list[float] = Field(default_factory=list)
    daily_precip_mm: list[float] = Field(default_factory=list)
    dates: list[str] = Field(default_factory=list)
    summary: str | None = None
    avg_high_c: float | None = None
    avg_low_c: float | None = None
    rainy_days: int | None = None


class BestSeasonInfo(BaseModel):
    best_months: list[str] = Field(default_factory=list)
    avoid_months: list[str] = Field(default_factory=list)
    reason: str | None = None


class CountryProfile(BaseModel):
    name: str
    official_name: str | None = None
    code_alpha2: str | None = None
    code_alpha3: str | None = None
    capital: str | None = None
    region: str | None = None
    subregion: str | None = None
    population: int | None = None
    area_km2: float | None = None
    languages: dict[str, str] = Field(default_factory=dict)
    currencies: dict[str, dict[str, str]] = Field(default_factory=dict)
    timezones: list[str] = Field(default_factory=list)
    flag_emoji: str | None = None
    flag_svg: str | None = None
    calling_code: str | None = None
    drives_on: str | None = None
    plug_types: list[str] = Field(default_factory=list)


class DestinationIntel(BaseModel):
    country: CountryProfile
    visa: VisaInfo | None = None
    weather: WeatherSummary | None = None
    best_season: BestSeasonInfo | None = None
    safety_tips: list[str] = Field(default_factory=list)
    cultural_etiquette: list[str] = Field(default_factory=list)
    common_scams: list[str] = Field(default_factory=list)
    tipping_norms: str | None = None
    emergency_numbers: dict[str, str] = Field(default_factory=dict)
    summary: str | None = None
    wikivoyage_url: str | None = None

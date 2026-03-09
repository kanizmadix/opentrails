"""Destination intelligence and country profile models."""
from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class VisaInfo(BaseModel):
    requirement: str = Field(..., description="visa-free / visa-on-arrival / e-visa / required / unknown")
    max_stay_days: Optional[int] = None
    notes: Optional[str] = None
    source: Optional[str] = None


class WeatherSummary(BaseModel):
    daily_high_c: List[float] = Field(default_factory=list)
    daily_low_c: List[float] = Field(default_factory=list)
    daily_precip_mm: List[float] = Field(default_factory=list)
    dates: List[str] = Field(default_factory=list)
    summary: Optional[str] = None
    avg_high_c: Optional[float] = None
    avg_low_c: Optional[float] = None
    rainy_days: Optional[int] = None


class BestSeasonInfo(BaseModel):
    best_months: List[str] = Field(default_factory=list)
    avoid_months: List[str] = Field(default_factory=list)
    reason: Optional[str] = None


class CountryProfile(BaseModel):
    name: str
    official_name: Optional[str] = None
    code_alpha2: Optional[str] = None
    code_alpha3: Optional[str] = None
    capital: Optional[str] = None
    region: Optional[str] = None
    subregion: Optional[str] = None
    population: Optional[int] = None
    area_km2: Optional[float] = None
    languages: Dict[str, str] = Field(default_factory=dict)
    currencies: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    timezones: List[str] = Field(default_factory=list)
    flag_emoji: Optional[str] = None
    flag_svg: Optional[str] = None
    calling_code: Optional[str] = None
    drives_on: Optional[str] = None
    plug_types: List[str] = Field(default_factory=list)


class DestinationIntel(BaseModel):
    country: CountryProfile
    visa: Optional[VisaInfo] = None
    weather: Optional[WeatherSummary] = None
    best_season: Optional[BestSeasonInfo] = None
    safety_tips: List[str] = Field(default_factory=list)
    cultural_etiquette: List[str] = Field(default_factory=list)
    common_scams: List[str] = Field(default_factory=list)
    tipping_norms: Optional[str] = None
    emergency_numbers: Dict[str, str] = Field(default_factory=dict)
    summary: Optional[str] = None
    wikivoyage_url: Optional[str] = None

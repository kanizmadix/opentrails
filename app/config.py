"""Application configuration via pydantic-settings."""
from __future__ import annotations

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All runtime configuration. Reads from environment / .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Anthropic
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-sonnet-4-6"
    CLAUDE_MAX_TOKENS: int = 2048

    # Optional travel API credentials (free tiers)
    AMADEUS_CLIENT_ID: str = ""
    AMADEUS_CLIENT_SECRET: str = ""
    KIWI_API_KEY: str = ""
    OPENTRIPMAP_API_KEY: str = ""

    # App
    APP_NAME: str = "OpenTrails"
    APP_VERSION: str = "0.1.0"
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str = "sqlite:///./data/opentrails.db"
    CORS_ORIGINS: str = "*"
    RATE_LIMIT_PER_MINUTE: int = 120
    CACHE_TTL_SECONDS: int = 900

    # External API base URLs (overridable for tests)
    NOMINATIM_BASE: str = "https://nominatim.openstreetmap.org"
    OVERPASS_BASE: str = "https://overpass-api.de/api/interpreter"
    OPENTRIPMAP_BASE: str = "https://api.opentripmap.com/0.1"
    OPEN_METEO_BASE: str = "https://api.open-meteo.com/v1"
    REST_COUNTRIES_BASE: str = "https://restcountries.com/v3.1"
    FRANKFURTER_BASE: str = "https://api.frankfurter.app"
    WIKIPEDIA_BASE: str = "https://en.wikipedia.org/api/rest_v1"
    WIKIVOYAGE_BASE: str = "https://en.wikivoyage.org/api/rest_v1"
    AMADEUS_BASE: str = "https://test.api.amadeus.com"
    KIWI_BASE: str = "https://api.tequila.kiwi.com"

    # User-Agent for OSM-family APIs (their policy)
    USER_AGENT: str = "OpenTrails/0.1 (https://github.com/kanizmadix/opentrails)"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

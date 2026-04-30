"""Pytest fixtures for OpenTrails."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Ensure app package is importable when running pytest from repo root.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def _temp_db(tmp_path, monkeypatch):
    """Point the SQLite DATABASE_URL at a fresh tmp file for every test."""
    db_path = tmp_path / "opentrails.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")

    # Reset settings + cache singletons that read env at module import time.
    from app import config as _config
    _config.get_settings.cache_clear()
    _config.settings = _config.get_settings()

    # Patch settings on already-imported modules.
    for mod_name in [
        "app.config", "app.db", "app.utils.cache", "app.logger", "app.rate_limiter",
        "app.utils.http", "app.services.nominatim", "app.services.overpass",
        "app.services.opentripmap", "app.services.open_meteo", "app.services.rest_countries",
        "app.services.frankfurter", "app.services.wikipedia", "app.services.wikivoyage",
        "app.services.amadeus", "app.services.kiwi", "app.services.providers",
        "app.ai.claude_client",
    ]:
        m = sys.modules.get(mod_name)
        if m and hasattr(m, "settings"):
            m.settings = _config.settings

    from app.db import init_db
    init_db()

    # Reset in-memory cache between tests.
    from app.utils.cache import cache as _cache
    _cache._store.clear()
    yield
    _cache._store.clear()


@pytest.fixture
def mock_claude(monkeypatch):
    """Patch the Claude client to a MagicMock so AI tests don't hit network."""
    fake_client = MagicMock()
    from app.ai import claude_client as cc

    cc.get_client.cache_clear()
    monkeypatch.setattr(cc, "get_client", lambda: fake_client)

    def _set_response(text: str):
        msg = MagicMock()
        block = MagicMock()
        block.text = text
        msg.content = [block]
        usage = MagicMock()
        usage.input_tokens = 100
        usage.output_tokens = 200
        usage.cache_read_input_tokens = 0
        usage.cache_creation_input_tokens = 0
        msg.usage = usage
        fake_client.messages.create.return_value = msg

    fake_client.set_response = _set_response
    return fake_client


@pytest.fixture
def app_client():
    """Return a TestClient bound to the FastAPI app."""
    from fastapi.testclient import TestClient

    from app.main import app
    return TestClient(app)


@pytest.fixture
def disable_rate_limit():
    """Make rate limiter unbounded for tests."""
    from app.main import app as _app
    for mw in getattr(_app, "user_middleware", []):
        if mw.cls.__name__ == "TokenBucketLimiter":
            mw.kwargs["requests_per_minute"] = 10**9
    # Patch any already-built middleware stack instance.
    stack = getattr(_app, "middleware_stack", None)
    while stack is not None:
        inner = getattr(stack, "app", None)
        if hasattr(stack, "limit"):
            stack.limit = 10**9
        if inner is None or inner is stack:
            break
        stack = inner
    yield


@pytest.fixture(autouse=True)
def _no_provider_keys(monkeypatch):
    """Force tests into mock-provider mode by clearing optional provider keys."""
    for k in ("AMADEUS_CLIENT_ID", "AMADEUS_CLIENT_SECRET", "KIWI_API_KEY", "OPENTRIPMAP_API_KEY"):
        os.environ.pop(k, None)
    from app.config import settings
    settings.AMADEUS_CLIENT_ID = ""
    settings.AMADEUS_CLIENT_SECRET = ""
    settings.KIWI_API_KEY = ""
    settings.OPENTRIPMAP_API_KEY = ""

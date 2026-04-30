"""Tests for the /api/health endpoint."""
from __future__ import annotations


def test_health_returns_ok(app_client, disable_rate_limit):
    resp = app_client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["name"]
    assert "version" in body
    assert body["claude_configured"] is True  # set by conftest fixture

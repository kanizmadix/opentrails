"""Shared httpx async client wrapper with sane defaults and retries."""
from __future__ import annotations

import asyncio
from typing import Any

import httpx

from app.config import settings
from app.exceptions import UpstreamAPIError
from app.logger import get_logger

log = get_logger(__name__)

_DEFAULT_TIMEOUT = httpx.Timeout(15.0, connect=5.0)
_DEFAULT_HEADERS = {
    "User-Agent": settings.USER_AGENT,
    "Accept": "application/json",
}


async def get_json(url: str, *, params: dict | None = None, headers: dict | None = None,
                   timeout: httpx.Timeout | None = None, retries: int = 2) -> Any:
    """GET JSON with retries on 5xx / transient errors."""
    merged_headers = {**_DEFAULT_HEADERS, **(headers or {})}
    last_exc: Exception | None = None
    async with httpx.AsyncClient(timeout=timeout or _DEFAULT_TIMEOUT) as client:
        for attempt in range(retries + 1):
            try:
                resp = await client.get(url, params=params, headers=merged_headers)
                if resp.status_code >= 500:
                    raise UpstreamAPIError(f"{url} returned {resp.status_code}")
                resp.raise_for_status()
                return resp.json()
            except (httpx.TransportError, UpstreamAPIError) as exc:
                last_exc = exc
                if attempt < retries:
                    await asyncio.sleep(0.5 * (2 ** attempt))
                    continue
                log.warning("upstream_failed", url=url, attempts=attempt + 1, err=str(exc))
                raise UpstreamAPIError(f"upstream call failed: {url}") from exc
            except httpx.HTTPStatusError as exc:
                raise UpstreamAPIError(f"{url} returned {exc.response.status_code}") from exc
    raise UpstreamAPIError(str(last_exc) if last_exc else f"unknown error calling {url}")


async def post_json(url: str, *, json: dict | None = None, data: dict | None = None,
                    headers: dict | None = None, timeout: httpx.Timeout | None = None) -> Any:
    merged_headers = {**_DEFAULT_HEADERS, **(headers or {})}
    async with httpx.AsyncClient(timeout=timeout or _DEFAULT_TIMEOUT) as client:
        try:
            resp = await client.post(url, json=json, data=data, headers=merged_headers)
            resp.raise_for_status()
            if resp.headers.get("content-type", "").startswith("application/json"):
                return resp.json()
            return resp.text
        except httpx.HTTPError as exc:
            raise UpstreamAPIError(f"POST {url} failed: {exc}") from exc

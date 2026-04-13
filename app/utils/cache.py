"""Simple in-memory TTL cache for upstream API responses."""
from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable
from typing import Any

from app.config import settings


class TTLCache:
    def __init__(self, default_ttl: int | None = None) -> None:
        self._store: dict[str, tuple[float, Any]] = {}
        self._lock = asyncio.Lock()
        self._default_ttl = default_ttl or settings.CACHE_TTL_SECONDS

    def _now(self) -> float:
        return time.monotonic()

    async def get(self, key: str) -> Any | None:
        async with self._lock:
            entry = self._store.get(key)
            if not entry:
                return None
            expires_at, value = entry
            if self._now() > expires_at:
                self._store.pop(key, None)
                return None
            return value

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        async with self._lock:
            self._store[key] = (self._now() + (ttl or self._default_ttl), value)

    async def get_or_set(self, key: str, fetch: Callable[[], Awaitable[Any]], ttl: int | None = None) -> Any:
        existing = await self.get(key)
        if existing is not None:
            return existing
        value = await fetch()
        await self.set(key, value, ttl)
        return value


cache = TTLCache()

"""Simple in-memory token-bucket rate limiter middleware (per-IP)."""
from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config import settings


class TokenBucketLimiter(BaseHTTPMiddleware):
    """Per-IP sliding window: max N requests per 60s."""

    def __init__(self, app, *, requests_per_minute: int | None = None) -> None:
        super().__init__(app)
        self.window = 60.0
        self.limit = requests_per_minute or settings.RATE_LIMIT_PER_MINUTE
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        ip = request.client.host if request.client else "anon"
        now = time.monotonic()
        bucket = self._hits[ip]
        cutoff = now - self.window
        while bucket and bucket[0] < cutoff:
            bucket.popleft()
        if len(bucket) >= self.limit:
            return JSONResponse(
                status_code=429,
                content={"error": {"code": "rate_limit_exceeded", "message": f"Max {self.limit} req/min"}},
            )
        bucket.append(now)
        return await call_next(request)

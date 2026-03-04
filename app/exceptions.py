"""Domain exceptions and FastAPI handlers."""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class OpenTrailsError(Exception):
    """Base exception."""

    status_code: int = 500
    code: str = "internal_error"

    def __init__(self, message: str, *, code: str | None = None, status_code: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        if code:
            self.code = code
        if status_code:
            self.status_code = status_code


class UpstreamAPIError(OpenTrailsError):
    status_code = 502
    code = "upstream_api_error"


class NotFoundError(OpenTrailsError):
    status_code = 404
    code = "not_found"


class ValidationError(OpenTrailsError):
    status_code = 422
    code = "validation_error"


class RateLimitExceeded(OpenTrailsError):
    status_code = 429
    code = "rate_limit_exceeded"


class ConfigurationError(OpenTrailsError):
    status_code = 503
    code = "configuration_error"


def install_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(OpenTrailsError)
    async def _handle(_: Request, exc: OpenTrailsError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

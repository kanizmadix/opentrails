"""OpenTrails — FastAPI application entrypoint with auto-router discovery."""
from __future__ import annotations

import importlib
import pkgutil
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import api as api_pkg
from app.config import settings
from app.db import init_db
from app.exceptions import install_exception_handlers
from app.logger import configure_logging, get_logger
from app.models.common import HealthResponse
from app.rate_limiter import TokenBucketLimiter

configure_logging()
log = get_logger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
TEMPLATES_DIR = FRONTEND_DIR / "templates"
STATIC_DIR = FRONTEND_DIR / "static"


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Open-API travel platform: flights, hotels, attractions, AI itineraries.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[s.strip() for s in settings.CORS_ORIGINS.split(",")] or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(TokenBucketLimiter)
    install_exception_handlers(app)

    @app.middleware("http")
    async def _request_log(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        log.info(
            "request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            elapsed_ms=elapsed_ms,
        )
        return response

    init_db()
    _mount_static_and_templates(app)
    _auto_register_routers(app)
    _register_health(app)
    _register_pages(app)
    return app


def _mount_static_and_templates(app: FastAPI) -> None:
    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    app.state.templates = Jinja2Templates(directory=str(TEMPLATES_DIR)) if TEMPLATES_DIR.exists() else None


def _auto_register_routers(app: FastAPI) -> None:
    """Auto-discover and register every `router` exported from app/api/*.py."""
    for mod_info in pkgutil.iter_modules(api_pkg.__path__):
        if mod_info.name.startswith("_"):
            continue
        module = importlib.import_module(f"{api_pkg.__name__}.{mod_info.name}")
        router = getattr(module, "router", None)
        if router is None:
            continue
        prefix = getattr(module, "PREFIX", f"/api/{mod_info.name}")
        tags = getattr(module, "TAGS", [mod_info.name])
        app.include_router(router, prefix=prefix, tags=tags)
        log.info("router_registered", module=mod_info.name, prefix=prefix)


def _register_health(app: FastAPI) -> None:
    @app.get("/api/health", response_model=HealthResponse, tags=["health"])
    async def health() -> HealthResponse:
        return HealthResponse(
            name=settings.APP_NAME,
            version=settings.APP_VERSION,
            db=settings.DATABASE_URL,
            claude_configured=bool(settings.ANTHROPIC_API_KEY),
        )


def _register_pages(app: FastAPI) -> None:
    """Serve the frontend HTML pages (templates live in frontend/templates)."""

    @app.get("/", response_class=HTMLResponse, tags=["pages"])
    async def home(request: Request):
        if app.state.templates is None:
            return HTMLResponse("<h1>OpenTrails</h1><p>Frontend not yet built.</p>")
        return app.state.templates.TemplateResponse("home.html", {"request": request})


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

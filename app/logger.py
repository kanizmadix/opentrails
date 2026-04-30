"""Structured JSON logging for OpenTrails."""
from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from app.config import settings


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        for key, val in record.__dict__.items():
            if key in {
                "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
                "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
                "created", "msecs", "relativeCreated", "thread", "threadName",
                "processName", "process", "asctime", "message", "taskName",
            }:
                continue
            try:
                json.dumps(val)
                payload[key] = val
            except (TypeError, ValueError):
                payload[key] = repr(val)
        return json.dumps(payload, default=str)


_configured = False


def configure_logging() -> None:
    global _configured
    if _configured:
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    _configured = True


class _KwargAdapter(logging.LoggerAdapter):
    """Allow ``log.info("event", key=val)`` style structured logging.

    Forwards reserved logging kwargs (``exc_info``, ``stack_info``, ``stacklevel``,
    ``extra``) untouched and packages everything else into ``extra`` so the
    JSONFormatter can render the fields.
    """

    _RESERVED = {"exc_info", "stack_info", "stacklevel", "extra"}
    _LOGRECORD_ATTRS = {
        "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
        "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
        "created", "msecs", "relativeCreated", "thread", "threadName",
        "processName", "process", "asctime", "message", "taskName",
    }

    def process(self, msg, kwargs):
        passthrough = {k: kwargs.pop(k) for k in list(kwargs) if k in self._RESERVED}
        if kwargs:
            extra = dict(passthrough.get("extra") or {})
            for k, v in kwargs.items():
                # Avoid colliding with LogRecord built-ins.
                key = f"ctx_{k}" if k in self._LOGRECORD_ATTRS else k
                extra[key] = v
            passthrough["extra"] = extra
            kwargs.clear()
        kwargs.update(passthrough)
        return msg, kwargs


def get_logger(name: str) -> _KwargAdapter:
    configure_logging()
    return _KwargAdapter(logging.getLogger(name), {})

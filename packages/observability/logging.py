"""
Structured logging utilities.

Responsibilities:
- configure structured JSON logging
- attach request_id to logs
- support correlation across services

Future:
- log enrichment
- error aggregation
"""

from __future__ import annotations

import json
import logging
import sys
import time
from contextvars import ContextVar
from typing import Any
from apps.api.config import settings
REQUEST_ID_CTX: ContextVar[str | None] = ContextVar("request_id", default=None)
TRACE_ID_CTX: ContextVar[str | None] = ContextVar("trace_id", default=None)
SPAN_ID_CTX: ContextVar[str | None] = ContextVar("span_id", default=None)

DEFAULT_LOG_LEVEL = settings.LOG_LEVEL


def set_request_context(
    *,
    request_id: str | None = None,
    trace_id: str | None = None,
    span_id: str | None = None,
) -> None:
    if request_id is not None:
        REQUEST_ID_CTX.set(request_id)
    if trace_id is not None:
        TRACE_ID_CTX.set(trace_id)
    if span_id is not None:
        SPAN_ID_CTX.set(span_id)


def clear_request_context() -> None:
    REQUEST_ID_CTX.set(None)
    TRACE_ID_CTX.set(None)
    SPAN_ID_CTX.set(None)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": REQUEST_ID_CTX.get(),
            "trace_id": TRACE_ID_CTX.get(),
            "span_id": SPAN_ID_CTX.get(),
            "module": record.module,
            "func": record.funcName,
            "line": record.lineno,
        }

        extras = {
            k: v
            for k, v in record.__dict__.items()
            if k
            not in {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
            }
        }
        payload.update(extras)

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


def configure_logging(level: str = DEFAULT_LOG_LEVEL) -> None:
    root = logging.getLogger()
    root.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root.handlers.clear()
    root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
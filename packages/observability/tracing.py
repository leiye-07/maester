"""
Tracing integration.

Responsibilities:
- OpenTelemetry instrumentation
- trace propagation across services
- connect API + worker traces

Future:
- metrics integration
- span-level cost attribution
"""
from __future__ import annotations

import time
from contextlib import contextmanager
from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from typing import Any, Generator

from packages.common.ids import new_id
from packages.observability.logging import get_logger, set_request_context

logger = get_logger(__name__)

TRACE_ID_CTX: ContextVar[str | None] = ContextVar("trace_id", default=None)
SPAN_ID_CTX: ContextVar[str | None] = ContextVar("span_id", default=None)
PARENT_SPAN_ID_CTX: ContextVar[str | None] = ContextVar("parent_span_id", default=None)


def current_trace_id() -> str | None:
    return TRACE_ID_CTX.get()

def current_span_id() -> str | None:
    return SPAN_ID_CTX.get()

def current_parent_span_id() -> str | None:
    return PARENT_SPAN_ID_CTX.get()


def start_trace(trace_id: str | None = None) -> str:
    """
    Start a new trace and bind it into the current context.
    """
    tid = trace_id or new_id()
    TRACE_ID_CTX.set(tid)

    # Keep logging context aligned with tracing context
    set_request_context(trace_id=tid)

    logger.info(
        "trace_started",
        extra={
            "trace_id": tid,
        },
    )
    return tid


def clear_trace() -> None:
    TRACE_ID_CTX.set(None)
    SPAN_ID_CTX.set(None)
    PARENT_SPAN_ID_CTX.set(None)


@dataclass(slots=True)
class SpanResult:
    trace_id: str
    span_id: str
    parent_span_id: str | None
    name: str
    started_at_ms: int
    ended_at_ms: int
    duration_ms: int
    status: str
    attributes: dict[str, Any] = field(default_factory=dict)

    def set_attribute(self, key: str, value: Any) -> None:
        self.attributes[key] = value

    def set_attributes(self, **kwargs: Any) -> None:
        self.attributes.update(kwargs)

    def as_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "name": self.name,
            "started_at_ms": self.started_at_ms,
            "ended_at_ms": self.ended_at_ms,
            "duration_ms": self.duration_ms,
            "status": self.status,
            "attributes": self.attributes,
        }


@contextmanager
def span(name: str, **fields: Any) -> Generator[SpanResult, None, None]:
    """
    Create a timed span within the current trace.

    Emits structured logs for:
    - span_started
    - span_finished
    - span_failed
    """
    trace_id = TRACE_ID_CTX.get() or start_trace()
    parent_span_id = SPAN_ID_CTX.get()
    span_id = new_id()

    span_token: Token[str | None] = SPAN_ID_CTX.set(span_id)
    parent_token: Token[str | None] = PARENT_SPAN_ID_CTX.set(parent_span_id)

    # Keep logging context aligned
    set_request_context(trace_id=trace_id, span_id=span_id)

    started_at_ms = time.time_ns() // 1_000_000

    logger.info(
        "span_started",
        extra={
            "span_name": name,
            "trace_id": trace_id,
            "span_id": span_id,
            "parent_span_id": parent_span_id,
            **fields,
        },
    )

    result = SpanResult(
        trace_id=trace_id,
        span_id=span_id,
        parent_span_id=parent_span_id,
        name=name,
        started_at_ms=started_at_ms,
        ended_at_ms=started_at_ms,
        duration_ms=0,
        status="started",
    )

    try:
        yield result
    except Exception as exc:
        ended_at_ms = time.time_ns() // 1_000_000
        result.ended_at_ms = ended_at_ms
        result.duration_ms = ended_at_ms - started_at_ms
        result.status = "error"

        logger.exception(
            "span_failed",
            extra={
                "span_name": name,
                "trace_id": trace_id,
                "span_id": span_id,
                "parent_span_id": parent_span_id,
                "duration_ms": result.duration_ms,
                "error_type": exc.__class__.__name__,
                **fields,
            },
        )
        raise
    else:
        ended_at_ms = time.time_ns() // 1_000_000
        result.ended_at_ms = ended_at_ms
        result.duration_ms = ended_at_ms - started_at_ms
        result.status = "ok"

        logger.info(
            "span_finished",
            extra={
                "span_name": name,
                "trace_id": trace_id,
                "span_id": span_id,
                "parent_span_id": parent_span_id,
                "duration_ms": result.duration_ms,
                **fields,
            },
        )
    finally:
        SPAN_ID_CTX.reset(span_token)
        PARENT_SPAN_ID_CTX.reset(parent_token)

        # Restore logging context to parent span
        restored_span_id = SPAN_ID_CTX.get()
        set_request_context(trace_id=trace_id, span_id=restored_span_id)
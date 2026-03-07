"""
API middleware stack.

Responsibilities:
- Request ID generation and propagation
- Structured request logging
- Tenant authentication via API key
- Rate limiting hooks

V0 implementation:
- Request ID middleware only

Future:
- cost metering hooks
- tenant budget enforcement
"""

from __future__ import annotations

from typing import Callable

from fastapi import Request, Response

from packages.common.ids import new_id
from packages.observability.logging import clear_request_context, set_request_context
from packages.observability.tracing import clear_trace, start_trace


async def request_context_middleware(
    request: Request,
    call_next: Callable,
) -> Response:
    request_id = new_id()
    trace_id = start_trace()

    set_request_context(
        request_id=request_id,
        trace_id=trace_id,
    )

    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Trace-ID"] = trace_id
        return response
    finally:
        clear_request_context()
        clear_trace()
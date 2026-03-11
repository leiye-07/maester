"""
FastAPI application entrypoint.

Responsibilities:
- Initialize API application
- Attach middleware (request id, auth, logging)
- Register route modules
- Provide health and readiness endpoints

Future extensions:
- Tenant API key authentication
- Rate limiting
- Request tracing propagation
"""
from __future__ import annotations

from fastapi import FastAPI

from apps.api.config import settings
from apps.api.middleware import request_context_middleware
from apps.api.routes.health import router as health_router
from apps.api.routes.reliable_completion import router as reliable_completion_router
from apps.api.routes.prompted_completion import router as prompted_completion_router
from packages.observability.logging import configure_logging

configure_logging(settings.LOG_LEVEL)

app = FastAPI(
    title="Maester API",
    description="AI Reliability Toolkit API",
    version="0.1.0",
)

app.middleware("http")(request_context_middleware)

app.include_router(health_router)
app.include_router(reliable_completion_router)
app.include_router(prompted_completion_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": settings.service_name}
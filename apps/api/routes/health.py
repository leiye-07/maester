"""
Health check endpoints.

Used by:
- load balancers
- container orchestrators
- uptime monitors
"""
from __future__ import annotations

from fastapi import APIRouter

from apps.api.config import settings
from packages.common.models import HealthStatus

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthStatus)
def health() -> HealthStatus:
    return HealthStatus(
        status="ok",
        service=settings.service_name,
        environment=settings.environment,
    )
"""
Core data models.

Planned tables:
- tenants
- api_keys
- projects
- documents
- document_chunks
- usage_ledger
- job_history

These represent the core domain entities
for the AI SaaS infrastructure blueprint.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class BaseEnvelope(BaseModel):
    id: str = Field(..., description="Unique object identifier")
    created_at: datetime = Field(default_factory=utc_now)


class HealthStatus(BaseModel):
    status: str
    service: str
    environment: str
"""
Worker configuration.

Responsibilities:
- queue connection configuration
- worker concurrency
- retry policies

Future:
- job retry configuration
- dead-letter queue support
"""

from __future__ import annotations

from pydantic import BaseSettings


class WorkerSettings(BaseSettings):
    service_name: str = "maester-worker"
    environment: str = "local"
    log_level: str = "INFO"
    default_model: str = "gpt-4.1-mini"
    default_fallback_model: str = "gpt-4.1-mini"

    openai_api_key: str | None = None
    anthropic_api_key: str | None = None

    class Config:
        env_file = ".env"

settings = WorkerSettings()
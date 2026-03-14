from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class ReplayRequestRecord:
    request_id: str
    prompt_name: str
    prompt_version: str
    prompt_hash: str
    rendered_prompt: str
    variables: dict[str, Any]
    requested_model: str
    resolved_model: str
    provider: str
    max_tokens: int

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ReplayResponseRecord:
    content: str
    cost: dict[str, Any]
    evaluation: dict[str, Any]
    trace_id: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ReplayRecord:
    request: ReplayRequestRecord
    response: ReplayResponseRecord
    created_at: str = field(default_factory=utc_now_iso)

    @property
    def request_id(self) -> str:
        return self.request.request_id

    def as_dict(self) -> dict[str, Any]:
        return {
            "request": self.request.as_dict(),
            "response": self.response.as_dict(),
            "created_at": self.created_at,
        }


@dataclass(slots=True)
class ReplayRunResult:
    request_id: str
    original: ReplayRecord
    replayed_response: ReplayResponseRecord
    comparison: dict[str, Any]
    replayed_at: str = field(default_factory=utc_now_iso)

    def as_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "original": self.original.as_dict(),
            "replayed_response": self.replayed_response.as_dict(),
            "comparison": self.comparison,
            "replayed_at": self.replayed_at,
        }

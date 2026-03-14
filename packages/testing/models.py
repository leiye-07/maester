from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class AITestCase:
    name: str
    prompt_name: str
    prompt_version: str
    variables: dict[str, Any]
    model: str
    max_tokens: int = 200
    expected_contains: list[str] = field(default_factory=list)
    max_response_chars: int | None = 500
    source_request_id: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class AITestResult:
    test_name: str
    passed: bool
    provider: str
    model: str
    prompt_name: str
    prompt_version: str
    trace_id: str | None
    cost: dict[str, Any]
    evaluation: dict[str, Any]
    details: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class AISuiteResult:
    suite_name: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    results: list[AITestResult]
    created_at: str = field(default_factory=utc_now_iso)

    @property
    def pass_rate(self) -> float:
        if self.total_cases == 0:
            return 0.0
        return round(self.passed_cases / self.total_cases, 4)

    def as_dict(self) -> dict[str, Any]:
        return {
            "suite_name": self.suite_name,
            "total_cases": self.total_cases,
            "passed_cases": self.passed_cases,
            "failed_cases": self.failed_cases,
            "pass_rate": self.pass_rate,
            "results": [result.as_dict() for result in self.results],
            "created_at": self.created_at,
        }

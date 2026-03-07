"""
This module composes multiple evaluation metrics into one result.
Instead of running checks separately, you call one evaluator.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from statistics import mean
from typing import Any

from packages.evaluation.metrics import (
    EvaluationMetric,
    contains_required_terms,
    max_length,
    non_empty,
)


@dataclass(slots=True)
class EvaluationInput:
    prompt: str
    response: str
    required_terms: list[str] | None = None
    max_response_chars: int | None = None


@dataclass(slots=True)
class EvaluationResult:
    status: str
    reliability_score: float
    metrics: list[EvaluationMetric]

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        return payload

# Evaluate against reliability metrics
class Evaluator:
    def evaluate(self, data: EvaluationInput) -> EvaluationResult:
        metrics: list[EvaluationMetric] = [non_empty(data.response)]

        if data.required_terms:
            metrics.append(contains_required_terms(data.response, data.required_terms))

        if data.max_response_chars is not None:
            metrics.append(max_length(data.response, data.max_response_chars))

        reliability_score = round(mean(m.score for m in metrics), 4)
        status = "pass" if all(m.passed for m in metrics) else "fail"

        return EvaluationResult(
            status=status,
            reliability_score=reliability_score,
            metrics=metrics,
        )
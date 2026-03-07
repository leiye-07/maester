"""
This module defines simple, composable evaluation primitives.
Evaluation here means: after the model returns an answer, do some checks on that answer.
This is the simplest version of reliability evaluation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(slots=True)
class EvaluationMetric:
    name: str
    score: float
    passed: bool
    reason: str | None = None

# Checks whether required keywords exist in the output.
def contains_required_terms(text: str, required_terms: Iterable[str]) -> EvaluationMetric:
    normalized = text.lower()
    missing = [term for term in required_terms if term.lower() not in normalized]
    passed = len(missing) == 0
    score = 1.0 if passed else max(0.0, 1.0 - (len(missing) / max(1, len(list(required_terms)))))

    return EvaluationMetric(
        name="contains_required_terms",
        score=score,
        passed=passed,
        reason=None if passed else f"Missing terms: {', '.join(missing)}",
    )

# Checks if output exceeds a max character length.
def max_length(text: str, max_chars: int) -> EvaluationMetric:
    passed = len(text) <= max_chars
    score = 1.0 if passed else max(0.0, max_chars / max(len(text), 1))
    return EvaluationMetric(
        name="max_length",
        score=score,
        passed=passed,
        reason=None if passed else f"Length {len(text)} exceeds max {max_chars}",
    )

# Checks whether the response is empty
def non_empty(text: str) -> EvaluationMetric:
    passed = bool(text and text.strip())
    return EvaluationMetric(
        name="non_empty",
        score=1.0 if passed else 0.0,
        passed=passed,
        reason=None if passed else "Response is empty",
    )
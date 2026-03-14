from __future__ import annotations

from typing import Any


def assert_non_empty(content: str) -> tuple[bool, dict[str, Any]]:
    passed = bool(content and content.strip())
    return passed, {
        "assertion": "non_empty",
        "passed": passed,
    }


def assert_contains_required_terms(
    content: str,
    required_terms: list[str],
) -> tuple[bool, dict[str, Any]]:
    if not required_terms:
        return True, {
            "assertion": "contains_required_terms",
            "passed": True,
            "missing_terms": [],
        }

    normalized = content.lower()
    missing = [term for term in required_terms if term.lower() not in normalized]
    passed = len(missing) == 0

    return passed, {
        "assertion": "contains_required_terms",
        "passed": passed,
        "missing_terms": missing,
    }


def assert_max_response_chars(
    content: str,
    max_response_chars: int | None,
) -> tuple[bool, dict[str, Any]]:
    if max_response_chars is None:
        return True, {
            "assertion": "max_response_chars",
            "passed": True,
            "max_response_chars": None,
            "actual_length": len(content),
        }

    actual_length = len(content)
    passed = actual_length <= max_response_chars

    return passed, {
        "assertion": "max_response_chars",
        "passed": passed,
        "max_response_chars": max_response_chars,
        "actual_length": actual_length,
    }


def run_assertions(
    *,
    content: str,
    expected_contains: list[str],
    max_response_chars: int | None,
) -> tuple[bool, dict[str, Any]]:
    checks: list[dict[str, Any]] = []

    non_empty_passed, non_empty_details = assert_non_empty(content)
    checks.append(non_empty_details)

    contains_passed, contains_details = assert_contains_required_terms(
        content,
        expected_contains,
    )
    checks.append(contains_details)

    max_len_passed, max_len_details = assert_max_response_chars(
        content,
        max_response_chars,
    )
    checks.append(max_len_details)

    passed = non_empty_passed and contains_passed and max_len_passed

    return passed, {
        "passed": passed,
        "checks": checks,
    }

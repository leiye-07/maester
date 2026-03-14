from __future__ import annotations

from packages.replay.models import ReplayRecord
from packages.testing.models import AITestCase


def build_test_case_from_replay(
    record: ReplayRecord,
    *,
    name: str | None = None,
    expected_contains: list[str] | None = None,
    max_response_chars: int | None = 500,
) -> AITestCase:
    """
    Promote a replay record into a reusable AI test case.

    This is the bridge between:
    production incident / replay artifact
    and
    repeatable regression test fixture
    """
    return AITestCase(
        name=name or f"replay_{record.request.request_id}",
        prompt_name=record.request.prompt_name,
        prompt_version=record.request.prompt_version,
        variables=dict(record.request.variables),
        model=record.request.requested_model,
        max_tokens=record.request.max_tokens,
        expected_contains=expected_contains or [],
        max_response_chars=max_response_chars,
        source_request_id=record.request.request_id,
    )

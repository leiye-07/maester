from __future__ import annotations

from packages.replay.models import (
    ReplayRecord,
    ReplayRequestRecord,
    ReplayResponseRecord,
)


class ReplayRecorder:
    """
    Converts a completed AI request into a replayable artifact.

    This lets us:
    - inspect the original request
    - rerun it later
    - compare original vs replayed output
    - promote replay records into test fixtures later
    """

    def build_record(
        self,
        *,
        request_id: str,
        prompt_name: str,
        prompt_version: str,
        prompt_hash: str,
        rendered_prompt: str,
        variables: dict[str, object],
        requested_model: str,
        resolved_model: str,
        provider: str,
        max_tokens: int,
        response_content: str,
        cost: dict[str, object],
        evaluation: dict[str, object],
        trace_id: str | None = None,
    ) -> ReplayRecord:
        request = ReplayRequestRecord(
            request_id=request_id,
            prompt_name=prompt_name,
            prompt_version=prompt_version,
            prompt_hash=prompt_hash,
            rendered_prompt=rendered_prompt,
            variables=dict(variables),
            requested_model=requested_model,
            resolved_model=resolved_model,
            provider=provider,
            max_tokens=max_tokens,
        )

        response = ReplayResponseRecord(
            content=response_content,
            cost=dict(cost),
            evaluation=dict(evaluation),
            trace_id=trace_id,
        )

        return ReplayRecord(
            request=request,
            response=response,
        )

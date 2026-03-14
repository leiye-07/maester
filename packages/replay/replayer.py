from __future__ import annotations

from packages.evaluation import EvaluationInput, Evaluator
from packages.model_gateway.client import ModelGateway
from packages.model_gateway.meter import CostMeter
from packages.replay.compare import ReplayComparator
from packages.replay.models import (
    ReplayRecord,
    ReplayResponseRecord,
    ReplayRunResult,
)
from packages.observability.logging import get_logger
from packages.observability.tracing import span

logger = get_logger(__name__)


class ReplayReplayer:
    """
    Re-runs a previously recorded AI request through the current model gateway.

    This allows us to:
    - reproduce historical responses
    - compare old vs new outputs
    - detect regressions
    - convert replay records into future test fixtures
    """

    def __init__(
        self,
        *,
        model_gateway: ModelGateway,
        meter: CostMeter,
        evaluator: Evaluator,
        comparator: ReplayComparator | None = None,
    ) -> None:
        self.model_gateway = model_gateway
        self.meter = meter
        self.evaluator = evaluator
        self.comparator = comparator or ReplayComparator()

    def replay(self, record: ReplayRecord) -> ReplayRunResult:
        logger.info(
            "replay_started",
            extra={
                "request_id": record.request.request_id,
                "prompt_name": record.request.prompt_name,
                "prompt_version": record.request.prompt_version,
                "requested_model": record.request.requested_model,
                "resolved_model": record.request.resolved_model,
                "provider": record.request.provider,
            },
        )

        with span(
            "replay_model_generate",
            request_id=record.request.request_id,
            prompt_name=record.request.prompt_name,
            prompt_version=record.request.prompt_version,
            requested_model=record.request.requested_model,
        ) as sp:
            model_response = self.model_gateway.generate(
                model=record.request.requested_model,
                prompt=record.request.rendered_prompt,
                max_tokens=record.request.max_tokens,
            )
            sp.set_attributes(
                provider=model_response.provider,
                resolved_model=model_response.model,
                input_tokens=model_response.usage.input_tokens,
                output_tokens=model_response.usage.output_tokens,
                total_tokens=model_response.usage.total_tokens,
            )

        with span(
            "replay_cost_metering",
            request_id=record.request.request_id,
            provider=model_response.provider,
            resolved_model=model_response.model,
        ) as sp:
            cost_record = self.meter.record(
                model=model_response.model,
                usage=model_response.usage,
            )
            sp.set_attributes(
                total_cost_usd=str(cost_record.total_cost_usd),
                input_cost_usd=str(cost_record.input_cost_usd),
                output_cost_usd=str(cost_record.output_cost_usd),
            )

        with span(
            "replay_evaluation",
            request_id=record.request.request_id,
            provider=model_response.provider,
            resolved_model=model_response.model,
        ) as sp:
            # Sprint 1: reuse simple evaluation pattern.
            # We preserve the original rendered prompt, but do not attempt
            # to reconstruct custom assertion logic beyond basic runtime
            # checks.
            evaluation = self.evaluator.evaluate(
                EvaluationInput(
                    prompt=record.request.rendered_prompt,
                    response=model_response.content,
                    max_response_chars=500,
                )
            )
            sp.set_attributes(
                evaluation_status=evaluation.status,
                reliability_score=evaluation.reliability_score,
            )

        replayed_response = ReplayResponseRecord(
            content=model_response.content,
            cost=cost_record.as_dict(),
            evaluation=evaluation.as_dict(),
            trace_id=None,
        )

        comparison = self.comparator.compare(
            original=record,
            replayed=replayed_response,
            replayed_provider=model_response.provider,
            replayed_model=model_response.model,
        )

        logger.info(
            "replay_finished",
            extra={
                "request_id": record.request.request_id,
                "comparison": comparison,
            },
        )

        return ReplayRunResult(
            request_id=record.request.request_id,
            original=record,
            replayed_response=replayed_response,
            comparison=comparison,
        )

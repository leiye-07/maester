"""
This is a Ai reliability demo
"""

from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from apps.api.config import settings
from apps.api.deps import (
    get_budget_guard,
    get_cost_meter,
    get_evaluator,
    get_model_gateway,
)
from packages.budgets.models import BudgetPolicy
from packages.budgets.service import RequestBudgetGuard
from packages.evaluation import EvaluationInput, Evaluator
from packages.model_gateway.client import ModelGateway
from packages.model_gateway.meter import CostMeter
from packages.observability.logging import get_logger
from packages.observability.tracing import current_trace_id, span

router = APIRouter(prefix="/v1", tags=["reliability"])
logger = get_logger(__name__)


class ReliableCompletionRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=4000)
    model: str | None = None
    max_tokens: int = Field(default=200, ge=1, le=2000)
    required_terms: list[str] | None = None
    max_response_chars: int | None = Field(default=500, ge=1)
    budget_scope: str | None = Field(default="demo")
    max_cost_usd: str | None = Field(default=None)
    allow_fallback_to_cheaper_model: bool = Field(default=True)


class ReliableCompletionResponse(BaseModel):
    provider: str
    model: str
    content: str
    trace_id: str | None
    cost: dict
    budget: dict
    evaluation: dict


def _fallback_model_for(model: str, allow_fallback: bool) -> str | None:
    if not allow_fallback:
        return None

    fallback_map = {
        "gpt-4.1": "gpt-4.1-mini",
        "claude-3-5-sonnet": "claude-3-5-haiku",
    }
    return fallback_map.get(model)


def _build_budget_policy(payload: ReliableCompletionRequest,
                         requested_model: str) -> BudgetPolicy | None:
    if payload.max_cost_usd is None:
        return None

    return BudgetPolicy(
        max_cost_usd=Decimal(payload.max_cost_usd),
        max_output_tokens=payload.max_tokens,
        fallback_model_if_over_budget=_fallback_model_for(
            requested_model,
            payload.allow_fallback_to_cheaper_model,
        ),
        scope_key=payload.budget_scope or "demo",
    )


@router.post("/reliable_completion", response_model=ReliableCompletionResponse)
def reliable_completion(
    payload: ReliableCompletionRequest,
    meter: CostMeter = Depends(get_cost_meter),
    evaluator: Evaluator = Depends(get_evaluator),
    model_gateway: ModelGateway = Depends(get_model_gateway),
    budget_guard: RequestBudgetGuard = Depends(get_budget_guard),
) -> ReliableCompletionResponse:
    requested_model = payload.model or settings.default_model
    budget_policy = _build_budget_policy(payload, requested_model)
    budget_decision = None

    logger.info(
        "reliable_completion_started",
        extra={
            "requested_model": requested_model,
            "max_tokens": payload.max_tokens,
            "has_required_terms": bool(payload.required_terms),
            "budget_enabled": budget_policy is not None,
            "budget_scope": payload.budget_scope,
            "max_cost_usd": payload.max_cost_usd,
        },
    )

    if budget_policy is not None:
        with span(
            "budget_check",
            requested_model=requested_model,
            max_tokens=payload.max_tokens,
            budget_scope=budget_policy.scope_key,
        ) as sp:
            budget_decision = budget_guard.check_request(
                requested_model=requested_model,
                prompt=payload.prompt,
                max_tokens=payload.max_tokens,
                policy=budget_policy,
            )
            sp.set_attributes(
                budget_allowed=budget_decision.allowed,
                budget_effective_model=budget_decision.effective_model,
                budget_fallback_applied=budget_decision.fallback_applied,
                estimated_total_cost_usd=str(
                    budget_decision.estimate.estimated_total_cost_usd
                ),
            )

        if not budget_decision.allowed:
            logger.info(
                "reliable_completion_blocked_by_budget",
                extra={
                    "requested_model": requested_model,
                    "budget_scope": budget_policy.scope_key,
                    "budget_decision": budget_decision.as_dict(),
                },
            )
            raise HTTPException(
                status_code=409,
                detail={
                    "message": "Request blocked by budget policy before provider dispatch",
                    "budget": budget_decision.as_dict(),
                },
            )

    effective_model = (
        budget_decision.effective_model
        if budget_decision is not None
        else requested_model
    )

    with span(
        "model_generate",
        requested_model=requested_model,
        effective_model=effective_model,
        max_tokens=payload.max_tokens,
    ) as sp:
        model_response = model_gateway.generate(
            model=effective_model,
            prompt=payload.prompt,
            max_tokens=payload.max_tokens,
        )
        sp.set_attributes(
            provider=model_response.provider,
            resolved_model=model_response.model,
            input_tokens=model_response.usage.input_tokens,
            output_tokens=model_response.usage.output_tokens,
            total_tokens=model_response.usage.total_tokens,
        )

    with span(
        "cost_metering",
        provider=model_response.provider,
        resolved_model=model_response.model,
    ) as sp:
        cost_record = meter.record(
            model=model_response.model,
            usage=model_response.usage,
        )
        sp.set_attributes(
            total_cost_usd=str(cost_record.total_cost_usd),
            input_cost_usd=str(cost_record.input_cost_usd),
            output_cost_usd=str(cost_record.output_cost_usd),
        )

    budget_payload: dict = {
        "enabled": budget_policy is not None,
    }
    if budget_decision is not None and budget_policy is not None:
        ledger_entry = budget_guard.record_actual_cost(
            scope_key=budget_policy.scope_key,
            actual_cost_usd=cost_record.total_cost_usd,
        )
        budget_payload = {
            "enabled": True,
            "scope_key": budget_policy.scope_key,
            "policy": {
                "max_cost_usd": str(budget_policy.max_cost_usd)
                if budget_policy.max_cost_usd is not None
                else None,
                "max_output_tokens": budget_policy.max_output_tokens,
                "fallback_model_if_over_budget":
                    budget_policy.fallback_model_if_over_budget,
            },
            **budget_decision.as_dict(),
            "actual_total_cost_usd": str(cost_record.total_cost_usd),
            "ledger": ledger_entry.as_dict(),
        }

    with span(
        "evaluation",
        provider=model_response.provider,
        resolved_model=model_response.model,
    ) as sp:
        evaluation = evaluator.evaluate(
            EvaluationInput(
                prompt=payload.prompt,
                response=model_response.content,
                required_terms=payload.required_terms,
                max_response_chars=payload.max_response_chars,
            )
        )
        sp.set_attributes(
            evaluation_status=evaluation.status,
            reliability_score=evaluation.reliability_score,
        )

    logger.info(
        "reliable_completion_finished",
        extra={
            "requested_model": requested_model,
            "provider": model_response.provider,
            "resolved_model": model_response.model,
            "usage": {
                "input_tokens": model_response.usage.input_tokens,
                "output_tokens": model_response.usage.output_tokens,
                "total_tokens": model_response.usage.total_tokens,
            },
            "cost": cost_record.as_dict(),
            "budget": budget_payload,
            "evaluation": evaluation.as_dict(),
        },
    )

    return ReliableCompletionResponse(
        provider=model_response.provider,
        model=model_response.model,
        content=model_response.content,
        trace_id=current_trace_id(),
        cost=cost_record.as_dict(),
        budget=budget_payload,
        evaluation=evaluation.as_dict(),
    )

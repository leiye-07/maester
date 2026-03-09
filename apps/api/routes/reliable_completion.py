"""
This is a Ai reliability demo
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from apps.api.config import settings
from apps.api.deps import get_cost_meter, get_evaluator, get_model_gateway
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


class ReliableCompletionResponse(BaseModel):
    provider: str
    model: str
    content: str
    trace_id: str | None
    cost: dict
    evaluation: dict


@router.post("/reliable_completion", response_model=ReliableCompletionResponse)
def reliable_completion(
    payload: ReliableCompletionRequest,
    meter: CostMeter = Depends(get_cost_meter),
    evaluator: Evaluator = Depends(get_evaluator),
    model_gateway: ModelGateway = Depends(get_model_gateway),
) -> ReliableCompletionResponse:
    requested_model = payload.model or settings.default_model

    logger.info(
        "reliable_completion_started",
        extra={
            "requested_model": requested_model,
            "max_tokens": payload.max_tokens,
            "has_required_terms": bool(payload.required_terms),
        },
    )

    with span(
        "model_generate",
        requested_model=requested_model,
        max_tokens=payload.max_tokens,
    ) as sp:
        model_response = model_gateway.generate(
            model=requested_model,
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
            "evaluation": evaluation.as_dict(),
        },
    )

    return ReliableCompletionResponse(
        provider=model_response.provider,
        model=model_response.model,
        content=model_response.content,
        trace_id=current_trace_id(),
        cost=cost_record.as_dict(),
        evaluation=evaluation.as_dict(),
    )
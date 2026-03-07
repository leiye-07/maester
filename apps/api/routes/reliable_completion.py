"""
This is a Ai reliability demo
"""

from __future__ import annotations

from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends

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
    max_response_chars: int | None = Field(default=500)


class ReliableCompletionResponse(BaseModel):
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
    model_name = payload.model or settings.default_model

    logger.info(
        "reliable_completion_started",
        extra={
            "model": model_name,
            "max_tokens": payload.max_tokens,
            "has_required_terms": bool(payload.required_terms),
        },
    )

    with span("model_generate"):
        model_response = model_gateway.generate(
            model=model_name,
            prompt=payload.prompt,
            max_tokens=payload.max_tokens,
        )

    with span("cost_metering"):
        cost_record = meter.record(
            model=model_response.model,
            usage=model_response.usage,
        )

    with span("evaluation"):
        evaluation = evaluator.evaluate(
            EvaluationInput(
                prompt=payload.prompt,
                response=model_response.content,
                required_terms=payload.required_terms,
                max_response_chars=payload.max_response_chars,
            )
        )

    logger.info(
        "reliable_completion_finished",
        extra={
            "model": model_response.model,
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
        model=model_response.model,
        content=model_response.content,
        trace_id=current_trace_id(),
        cost=cost_record.as_dict(),
        evaluation=evaluation.as_dict(),
    )

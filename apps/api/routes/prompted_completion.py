from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from apps.api.config import settings
from apps.api.deps import (
    get_cost_meter,
    get_evaluator,
    get_model_gateway,
    get_prompt_service,
)
from packages.evaluation import EvaluationInput, Evaluator
from packages.model_gateway.client import ModelGateway
from packages.model_gateway.meter import CostMeter
from packages.observability.logging import get_logger
from packages.observability.tracing import current_trace_id, span
from packages.prompt_registry import PromptService

router = APIRouter(prefix="/v1", tags=["prompt-registry"])
logger = get_logger(__name__)


class PromptedCompletionRequest(BaseModel):
    prompt_name: str
    prompt_version: str | None = None
    variables: dict[str, object] = Field(default_factory=dict)
    model: str | None = None
    max_tokens: int = Field(default=200, ge=1, le=2000)


class PromptedCompletionResponse(BaseModel):
    provider: str
    model: str
    trace_id: str | None
    prompt_name: str
    prompt_version: str
    prompt_hash: str
    content: str
    cost: dict
    evaluation: dict


@router.post("/prompted_completion", response_model=PromptedCompletionResponse)
def prompted_completion(
    payload: PromptedCompletionRequest,
    meter: CostMeter = Depends(get_cost_meter),
    evaluator: Evaluator = Depends(get_evaluator),
    model_gateway: ModelGateway = Depends(get_model_gateway),
    prompt_service: PromptService = Depends(get_prompt_service),
) -> PromptedCompletionResponse:
    requested_model = payload.model or settings.DEFAULT_MODEL

    with span(
        "prompt_render",
        prompt_name=payload.prompt_name,
        prompt_version=payload.prompt_version,
    ) as sp:
        rendered_prompt = prompt_service.render(
            name=payload.prompt_name,
            version=payload.prompt_version,
            variables=payload.variables,
        )
        sp.set_attributes(
            resolved_prompt_version=rendered_prompt.version,
            prompt_hash=rendered_prompt.hash,
        )

    with span(
        "model_generate",
        requested_model=requested_model,
        prompt_name=rendered_prompt.name,
        prompt_version=rendered_prompt.version,
    ) as sp:
        model_response = model_gateway.generate(
            model=requested_model,
            prompt=rendered_prompt.content,
            max_tokens=payload.max_tokens,
        )
        sp.set_attributes(
            provider=model_response.provider,
            resolved_model=model_response.model,
        )

    with span("cost_metering") as sp:
        cost_record = meter.record(
            model=model_response.model,
            usage=model_response.usage,
        )
        sp.set_attribute("total_cost_usd", str(cost_record.total_cost_usd))

    with span("evaluation") as sp:
        evaluation = evaluator.evaluate(
            EvaluationInput(
                prompt=rendered_prompt.content,
                response=model_response.content,
                max_response_chars=500,
            )
        )
        sp.set_attributes(
            evaluation_status=evaluation.status,
            reliability_score=evaluation.reliability_score,
        )

    logger.info(
        "prompted_completion_finished",
        extra={
            "prompt_name": rendered_prompt.name,
            "prompt_version": rendered_prompt.version,
            "prompt_hash": rendered_prompt.hash,
            "provider": model_response.provider,
            "resolved_model": model_response.model,
            "cost": cost_record.as_dict(),
            "evaluation": evaluation.as_dict(),
        },
    )

    return PromptedCompletionResponse(
        provider=model_response.provider,
        model=model_response.model,
        trace_id=current_trace_id(),
        prompt_name=rendered_prompt.name,
        prompt_version=rendered_prompt.version,
        prompt_hash=rendered_prompt.hash,
        content=model_response.content,
        cost=cost_record.as_dict(),
        evaluation=evaluation.as_dict(),
    )
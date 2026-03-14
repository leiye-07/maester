from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from apps.api.config import settings
from apps.api.deps import (
    get_cost_meter,
    get_evaluator,
    get_model_gateway,
    get_prompt_service,
    get_replay_recorder,
    get_replay_store,
)
from packages.common.ids import new_id
from packages.evaluation import EvaluationInput, Evaluator
from packages.model_gateway.client import ModelGateway
from packages.model_gateway.meter import CostMeter
from packages.observability.logging import get_logger
from packages.observability.tracing import current_trace_id, span
from packages.prompt_registry import PromptService
from packages.replay.recorder import ReplayRecorder
from packages.replay.store import ReplayStore

router = APIRouter(prefix="/v1", tags=["prompt-registry"])
logger = get_logger(__name__)


class PromptedCompletionRequest(BaseModel):
    prompt_name: str
    prompt_version: str | None = None
    variables: dict[str, object] = Field(default_factory=dict)
    model: str | None = None
    max_tokens: int = Field(default=200, ge=1, le=2000)


class PromptedCompletionResponse(BaseModel):
    request_id: str
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
    replay_recorder: ReplayRecorder = Depends(get_replay_recorder),
    replay_store: ReplayStore = Depends(get_replay_store),
) -> PromptedCompletionResponse:
    request_id = new_id()
    requested_model = payload.model or settings.DEFAULT_MODEL

    with span(
        "prompt_render",
        request_id=request_id,
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
        request_id=request_id,
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
            input_tokens=model_response.usage.input_tokens,
            output_tokens=model_response.usage.output_tokens,
            total_tokens=model_response.usage.total_tokens,
        )

    with span(
        "cost_metering",
        request_id=request_id,
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
        request_id=request_id,
        provider=model_response.provider,
        resolved_model=model_response.model,
    ) as sp:
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

    record = replay_recorder.build_record(
        request_id=request_id,
        prompt_name=rendered_prompt.name,
        prompt_version=rendered_prompt.version,
        prompt_hash=rendered_prompt.hash,
        rendered_prompt=rendered_prompt.content,
        variables=payload.variables,
        requested_model=requested_model,
        resolved_model=model_response.model,
        provider=model_response.provider,
        max_tokens=payload.max_tokens,
        response_content=model_response.content,
        cost=cost_record.as_dict(),
        evaluation=evaluation.as_dict(),
        trace_id=current_trace_id(),
    )
    replay_store.save(record)

    logger.info(
        "prompted_completion_finished",
        extra={
            "request_id": request_id,
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
        request_id=request_id,
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

"""
Async worker service.

Responsibilities:
- document ingestion jobs
- chunking + embedding pipelines
- background maintenance tasks

Future queue tasks:
- document_parse
- document_chunk
- embedding_generation
- vector_index_update

Queue backend:
- Redis
- ARQ or Celery (to be decided)
"""

from __future__ import annotations


from apps.worker.config import settings
from packages.common.ids import new_id
from packages.evaluation import EvaluationInput, Evaluator
from packages.model_gateway.client import ModelGateway
from packages.model_gateway.meter import CostMeter
from packages.observability.logging import configure_logging, get_logger, set_request_context, clear_request_context
from packages.observability.tracing import start_trace, clear_trace, span

configure_logging(settings.log_level)
logger = get_logger(__name__)


def run_demo_job(prompt: str) -> dict:
    request_id = new_id()
    trace_id = start_trace()
    set_request_context(request_id=request_id, trace_id=trace_id)

    gateway = ModelGateway()
    meter = CostMeter()
    evaluator = Evaluator()

    logger.info(
        "worker_job_started",
        extra={
            "service": settings.service_name,
            "prompt_preview": prompt[:80],
        },
    )

    try:
        with span("worker_model_generate", model=settings.default_model) as sp:
            response = gateway.generate(
                model=settings.default_model,
                prompt=prompt,
                max_tokens=200,
            )
            sp.set_attributes(
                provider=response.provider,
                resolved_model=response.model,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
            )

        with span("worker_cost_metering") as sp:
            cost = meter.record(
                model=response.model,
                usage=response.usage,
            )
            sp.set_attribute("total_cost_usd", str(cost.total_cost_usd))

        with span("worker_evaluation") as sp:
            evaluation = evaluator.evaluate(
                EvaluationInput(
                    prompt=prompt,
                    response=response.content,
                    required_terms=["Maester"],
                    max_response_chars=500,
                )
            )
            sp.set_attributes(
                reliability_status=evaluation.status,
                reliability_score=evaluation.reliability_score,
            )

        result = {
            "trace_id": trace_id,
            "model": response.model,
            "content": response.content,
            "cost": cost.as_dict(),
            "evaluation": evaluation.as_dict(),
        }

        logger.info(
            "worker_job_finished",
            extra=result,
        )
        return result
    finally:
        clear_request_context()
        clear_trace()


if __name__ == "__main__":
    demo = run_demo_job("Explain why AI reliability needs observability, cost metering, and evaluation.")
    print(demo)
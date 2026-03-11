"""
Dependency injection helpers for FastAPI routes.

Responsibilities:
- Provide tenant context
- Provide database connections
- Provide authenticated request context

Future additions:
- tenant resolution via API key
- usage metering injection
- request-scoped tracing context
"""
from __future__ import annotations

from packages.evaluation import Evaluator
from packages.model_gateway.client import ModelGateway
from packages.model_gateway.meter import CostMeter
from packages.prompt_registry import (
    PromptRegistry,
    PromptService,
    default_prompt_templates,
)

_meter = CostMeter()
_evaluator = Evaluator()
_model_gateway = ModelGateway()
_prompt_registry = PromptRegistry(default_prompt_templates())
_prompt_service = PromptService(_prompt_registry)


def get_cost_meter() -> CostMeter:
    return _meter

def get_evaluator() -> Evaluator:
    return _evaluator

def get_model_gateway() -> ModelGateway:
    return _model_gateway

def get_prompt_service() -> PromptService:
    return _prompt_service
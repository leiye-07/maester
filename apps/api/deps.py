from __future__ import annotations

from packages.evaluation import Evaluator
from packages.model_gateway.client import ModelGateway
from packages.model_gateway.meter import CostMeter
from packages.prompt_registry import (
    PromptRegistry,
    PromptService,
    default_prompt_templates,
)
from packages.replay.compare import ReplayComparator
from packages.replay.recorder import ReplayRecorder
from packages.replay.replayer import ReplayReplayer
from packages.replay.store import ReplayStore
from packages.testing.runner import AITestRunner

_meter = CostMeter()
_evaluator = Evaluator()
_model_gateway = ModelGateway()

_prompt_registry = PromptRegistry(default_prompt_templates())
_prompt_service = PromptService(_prompt_registry)

_replay_store = ReplayStore()
_replay_recorder = ReplayRecorder()
_replay_comparator = ReplayComparator()
_replay_replayer = ReplayReplayer(
    model_gateway=_model_gateway,
    meter=_meter,
    evaluator=_evaluator,
    comparator=_replay_comparator,
)

_ai_test_runner = AITestRunner(
    prompt_service=_prompt_service,
    model_gateway=_model_gateway,
    meter=_meter,
    evaluator=_evaluator,
)


def get_cost_meter() -> CostMeter:
    return _meter


def get_evaluator() -> Evaluator:
    return _evaluator


def get_model_gateway() -> ModelGateway:
    return _model_gateway


def get_prompt_service() -> PromptService:
    return _prompt_service


def get_replay_store() -> ReplayStore:
    return _replay_store


def get_replay_recorder() -> ReplayRecorder:
    return _replay_recorder


def get_replay_replayer() -> ReplayReplayer:
    return _replay_replayer


def get_ai_test_runner() -> AITestRunner:
    return _ai_test_runner

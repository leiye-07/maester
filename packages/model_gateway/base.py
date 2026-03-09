## Defines the common provider contract

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from packages.model_gateway.meter import TokenUsage


@dataclass(slots=True)
class GenerationRequest:
    model: str
    prompt: str
    max_tokens: int = 200


@dataclass(slots=True)
class GenerationResponse:
    provider: str
    model: str
    content: str
    usage: TokenUsage


class ModelProvider(Protocol):
    provider_name: str

    def supports_model(self, model: str) -> bool:
        ...

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        ...
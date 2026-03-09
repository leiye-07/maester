## 1. which provider to use
# 2. whether to fall back
# 3. how to route models cleanly
from __future__ import annotations

from dataclasses import dataclass

from packages.model_gateway.base import (
    GenerationRequest,
    GenerationResponse,
    ModelProvider,
)
from packages.observability.logging import get_logger

logger = get_logger(__name__)


@dataclass(slots=True)
class RoutingDecision:
    requested_model: str
    selected_provider: str
    selected_model: str
    fallback_used: bool = False


class NoProviderAvailableError(RuntimeError):
    pass


class ModelRouter:
    def __init__(self, providers: list[ModelProvider]) -> None:
        self.providers = providers

    def route(self, model: str) -> RoutingDecision:
        for provider in self.providers:
            if provider.supports_model(model):
                decision = RoutingDecision(
                    requested_model=model,
                    selected_provider=provider.provider_name,
                    selected_model=model,
                    fallback_used=False,
                )
                logger.info(
                    "model_routed",
                    extra={
                        "requested_model": decision.requested_model,
                        "selected_provider": decision.selected_provider,
                        "selected_model": decision.selected_model,
                        "fallback_used": decision.fallback_used,
                    },
                )
                return decision

        fallback = self._fallback_decision(model)
        logger.info(
            "model_routed_with_fallback",
            extra={
                "requested_model": fallback.requested_model,
                "selected_provider": fallback.selected_provider,
                "selected_model": fallback.selected_model,
                "fallback_used": fallback.fallback_used,
            },
        )
        return fallback

    def dispatch(self, request: GenerationRequest) -> GenerationResponse:
        decision = self.route(request.model)

        selected_provider = self._get_provider_by_name(decision.selected_provider)
        if selected_provider is None:
            raise NoProviderAvailableError(
                f"No provider found for routed provider: {decision.selected_provider}"
            )

        effective_request = GenerationRequest(
            model=decision.selected_model,
            prompt=request.prompt,
            max_tokens=request.max_tokens,
        )
        return selected_provider.generate(effective_request)

    def _fallback_decision(self, requested_model: str) -> RoutingDecision:
        # Simple starter fallback policy:
        # if unknown, fall back to gpt-4.1-mini on openai if available.
        for provider in self.providers:
            if provider.provider_name == "openai" and provider.supports_model("gpt-4.1-mini"):
                return RoutingDecision(
                    requested_model=requested_model,
                    selected_provider="openai",
                    selected_model="gpt-4.1-mini",
                    fallback_used=True,
                )

        raise NoProviderAvailableError(
            f"No provider available for requested model: {requested_model}"
        )

    def _get_provider_by_name(self, name: str) -> ModelProvider | None:
        for provider in self.providers:
            if provider.provider_name == name:
                return provider
        return None
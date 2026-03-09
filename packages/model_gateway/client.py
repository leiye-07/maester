"""
Model gateway abstraction.

Responsibilities:
- unify access to LLM providers
- enforce timeouts and retries
- support fallback providers

Future:
- OpenAI provider
- Anthropic provider
- local model provider
"""
from __future__ import annotations

from packages.model_gateway.base import GenerationRequest
from packages.model_gateway.provider_anthropic import AnthropicProvider
from packages.model_gateway.provider_openai import OpenAIProvider
from packages.model_gateway.router import ModelRouter


class ModelGateway:
    """
    Provider-agnostic gateway for AI model generation.

    Responsibilities:
    - accept a model request
    - route to the correct provider
    - apply fallback when necessary
    """

    def __init__(self) -> None:
        self.router = ModelRouter(
            providers=[
                OpenAIProvider(),
                AnthropicProvider(),
            ]
        )

    def generate(
        self,
        *,
        model: str,
        prompt: str,
        max_tokens: int = 200,
    ):
        request = GenerationRequest(
            model=model,
            prompt=prompt,
            max_tokens=max_tokens,
        )
        return self.router.dispatch(request)
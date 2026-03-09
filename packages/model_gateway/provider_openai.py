from __future__ import annotations

from packages.model_gateway.base import (
    GenerationRequest,
    GenerationResponse,
    ModelProvider,
)
from packages.model_gateway.meter import TokenUsage


class OpenAIProvider(ModelProvider):
    provider_name = "openai"

    _SUPPORTED_MODELS = {
        "gpt-4.1-mini",
        "gpt-4.1",
    }

    def supports_model(self, model: str) -> bool:
        return model in self._SUPPORTED_MODELS

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        content = (
            f"[OpenAI:{request.model}] Generated response for prompt: "
            f"{request.prompt[:120]}"
        )

        usage = TokenUsage(
            input_tokens=max(1, len(request.prompt.split()) * 2),
            output_tokens=min(request.max_tokens, max(20, len(content.split()) * 2)),
        )

        return GenerationResponse(
            provider=self.provider_name,
            model=request.model,
            content=content,
            usage=usage,
        )
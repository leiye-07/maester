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

from dataclasses import dataclass

from packages.model_gateway.meter import TokenUsage


@dataclass(slots=True)
class ModelResponse:
    model: str
    content: str
    usage: TokenUsage


class ModelGateway:
    """
    Demo model gateway.

    Replace with real OpenAI/Anthropic/local model adapters later.
    """

    def generate(
        self,
        *,
        model: str,
        prompt: str,
        max_tokens: int = 200,
    ) -> ModelResponse:
        response_text = (
            f"Maester response: processed prompt '{prompt[:120]}' "
            f"with reliability instrumentation enabled."
        )

        estimated_input_tokens = max(1, len(prompt.split()) * 2)
        estimated_output_tokens = min(max_tokens, max(20, len(response_text.split()) * 2))

        return ModelResponse(
            model=model,
            content=response_text,
            usage=TokenUsage(
                input_tokens=estimated_input_tokens,
                output_tokens=estimated_output_tokens,
            ),
        )
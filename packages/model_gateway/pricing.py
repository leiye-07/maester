"""
Model pricing registry.

Responsibilities:
- track token cost per provider
- support cost estimation
- enable budget enforcement

Future:
- dynamic provider pricing updates
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Final


@dataclass(frozen=True, slots=True)
class ModelPricing:
    model: str
    input_per_1k_tokens_usd: Decimal
    output_per_1k_tokens_usd: Decimal


DEFAULT_MODEL_PRICING: Final[dict[str, ModelPricing]] = {
    "gpt-4.1-mini": ModelPricing(
        model="gpt-4.1-mini",
        input_per_1k_tokens_usd=Decimal("0.0004"),
        output_per_1k_tokens_usd=Decimal("0.0016"),
    ),
    "gpt-4.1": ModelPricing(
        model="gpt-4.1",
        input_per_1k_tokens_usd=Decimal("0.0020"),
        output_per_1k_tokens_usd=Decimal("0.0080"),
    ),
}


def get_model_pricing(model: str) -> ModelPricing:
    if model not in DEFAULT_MODEL_PRICING:
        raise ValueError(f"No pricing configured for model: {model}")
    return DEFAULT_MODEL_PRICING[model]


def list_supported_models() -> list[str]:
    return sorted(DEFAULT_MODEL_PRICING.keys())
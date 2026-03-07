"""
Usage metering module.

Responsibilities:
- record token usage
- record request counts
- enforce per-tenant budgets

Future:
- cost alerts
- monthly usage aggregation
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from packages.model_gateway.pricing import ModelPricing, get_model_pricing


def _to_decimal(value: str | float | int) -> Decimal:
    return Decimal(str(value))


def _round_usd(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)


@dataclass(slots=True)
class TokenUsage:
    input_tokens: int
    output_tokens: int

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass(slots=True)
class CostRecord:
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    input_cost_usd: Decimal
    output_cost_usd: Decimal
    total_cost_usd: Decimal
    unit: str = "USD"

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["input_cost_usd"] = str(self.input_cost_usd)
        payload["output_cost_usd"] = str(self.output_cost_usd)
        payload["total_cost_usd"] = str(self.total_cost_usd)
        return payload


class CostMeter:
    def record(self, *, model: str, usage: TokenUsage) -> CostRecord:
        pricing = get_model_pricing(model)
        return self.record_with_pricing(pricing=pricing, usage=usage)

    def record_with_pricing(
        self,
        *,
        pricing: ModelPricing,
        usage: TokenUsage,
    ) -> CostRecord:
        input_cost = _round_usd(
            (_to_decimal(usage.input_tokens) / _to_decimal(1000))
            * pricing.input_per_1k_tokens_usd
        )
        output_cost = _round_usd(
            (_to_decimal(usage.output_tokens) / _to_decimal(1000))
            * pricing.output_per_1k_tokens_usd
        )
        total_cost = _round_usd(input_cost + output_cost)

        return CostRecord(
            model=pricing.model,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            total_tokens=usage.total_tokens,
            input_cost_usd=input_cost,
            output_cost_usd=output_cost,
            total_cost_usd=total_cost,
        )
from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal
from typing import Any

from packages.budgets.utils import round_usd


@dataclass(frozen=True, slots=True)
class BudgetPolicy:
    max_cost_usd: Decimal | None = None
    max_input_tokens: int | None = None
    max_output_tokens: int | None = None
    max_total_tokens: int | None = None
    fallback_model_if_over_budget: str | None = None
    scope_key: str = "default"

    def normalized(self) -> "BudgetPolicy":
        return BudgetPolicy(
            max_cost_usd=round_usd(self.max_cost_usd)
            if self.max_cost_usd is not None else None,
            max_input_tokens=self.max_input_tokens,
            max_output_tokens=self.max_output_tokens,
            max_total_tokens=self.max_total_tokens,
            fallback_model_if_over_budget=self.fallback_model_if_over_budget,
            scope_key=self.scope_key,
        )


@dataclass(frozen=True, slots=True)
class BudgetEstimate:
    model: str
    estimated_input_tokens: int
    estimated_output_tokens: int
    estimated_total_tokens: int
    estimated_input_cost_usd: Decimal
    estimated_output_cost_usd: Decimal
    estimated_total_cost_usd: Decimal

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["estimated_input_cost_usd"] = str(self.estimated_input_cost_usd)
        payload["estimated_output_cost_usd"] = str(self.estimated_output_cost_usd)
        payload["estimated_total_cost_usd"] = str(self.estimated_total_cost_usd)
        return payload


@dataclass(frozen=True, slots=True)
class BudgetDecision:
    allowed: bool
    reason: str | None
    effective_model: str
    fallback_applied: bool
    estimate: BudgetEstimate

    def as_dict(self) -> dict[str, Any]:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "effective_model": self.effective_model,
            "fallback_applied": self.fallback_applied,
            "estimate": self.estimate.as_dict(),
        }

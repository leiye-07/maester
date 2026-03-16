from __future__ import annotations

from decimal import Decimal
from math import ceil

from packages.budgets.errors import BudgetExceededError
from packages.budgets.ledger import BudgetLedgerEntry, InMemoryBudgetLedger
from packages.budgets.models import (BudgetDecision,
                                     BudgetEstimate,
                                     BudgetPolicy)
from packages.budgets.utils import (TOKENS_PER_CHAR_ESTIMATE,
                                    round_usd,
                                    to_decimal)
from packages.model_gateway.pricing import get_model_pricing


class RequestBudgetGuard:
    def __init__(self, *, ledger: InMemoryBudgetLedger | None = None) -> None:
        self.ledger = ledger or InMemoryBudgetLedger()

    def estimate_request(
        self,
        *,
        model: str,
        prompt: str,
        max_tokens: int,
    ) -> BudgetEstimate:
        estimated_input_tokens = self._estimate_input_tokens(prompt)
        estimated_output_tokens = max(1, max_tokens)
        estimated_total_tokens = estimated_input_tokens
        + estimated_output_tokens

        pricing = get_model_pricing(model)
        estimated_input_cost_usd = round_usd(
            (to_decimal(estimated_input_tokens) / to_decimal(1000))
            * pricing.input_per_1k_tokens_usd
        )
        estimated_output_cost_usd = round_usd(
            (to_decimal(estimated_output_tokens) / to_decimal(1000))
            * pricing.output_per_1k_tokens_usd
        )
        estimated_total_cost_usd = round_usd(
            estimated_input_cost_usd + estimated_output_cost_usd
        )

        return BudgetEstimate(
            model=model,
            estimated_input_tokens=estimated_input_tokens,
            estimated_output_tokens=estimated_output_tokens,
            estimated_total_tokens=estimated_total_tokens,
            estimated_input_cost_usd=estimated_input_cost_usd,
            estimated_output_cost_usd=estimated_output_cost_usd,
            estimated_total_cost_usd=estimated_total_cost_usd,
        )

    def check_request(
        self,
        *,
        requested_model: str,
        prompt: str,
        max_tokens: int,
        policy: BudgetPolicy,
    ) -> BudgetDecision:
        policy = policy.normalized()
        estimate = self.estimate_request(
            model=requested_model,
            prompt=prompt,
            max_tokens=max_tokens,
        )

        violation = self._first_violation(policy=policy, estimate=estimate)
        if violation is None:
            return BudgetDecision(
                allowed=True,
                reason=None,
                effective_model=requested_model,
                fallback_applied=False,
                estimate=estimate,
            )

        fallback_model = policy.fallback_model_if_over_budget
        if fallback_model and fallback_model != requested_model:
            fallback_estimate = self.estimate_request(
                model=fallback_model,
                prompt=prompt,
                max_tokens=max_tokens,
            )
            fallback_violation = self._first_violation(
                policy=policy,
                estimate=fallback_estimate,
            )
            if fallback_violation is None:
                return BudgetDecision(
                    allowed=True,
                    reason=f"requested model exceeded budget; downgraded via {violation}",
                    effective_model=fallback_model,
                    fallback_applied=True,
                    estimate=fallback_estimate,
                )

        return BudgetDecision(
            allowed=False,
            reason=violation,
            effective_model=requested_model,
            fallback_applied=False,
            estimate=estimate,
        )

    def enforce_request(
        self,
        *,
        requested_model: str,
        prompt: str,
        max_tokens: int,
        policy: BudgetPolicy,
    ) -> BudgetDecision:
        decision = self.check_request(
            requested_model=requested_model,
            prompt=prompt,
            max_tokens=max_tokens,
            policy=policy,
        )
        if not decision.allowed:
            raise BudgetExceededError(
                f"Request budget exceeded: {decision.reason}",
                decision=decision,
            )
        return decision

    def record_actual_cost(
        self,
        *,
        scope_key: str,
        actual_cost_usd: Decimal | str | float | int,
    ) -> BudgetLedgerEntry:
        return self.ledger.record(
            scope_key=scope_key,
            actual_cost_usd=to_decimal(actual_cost_usd),
        )

    @staticmethod
    def _estimate_input_tokens(prompt: str) -> int:
        return max(1, ceil(len(prompt) * float(TOKENS_PER_CHAR_ESTIMATE)))

    @staticmethod
    def _first_violation(
        *,
        policy: BudgetPolicy,
        estimate: BudgetEstimate,
    ) -> str | None:
        if (
            policy.max_input_tokens is not None
            and estimate.estimated_input_tokens > policy.max_input_tokens
        ):
            return (
                f"estimated input tokens {estimate.estimated_input_tokens} "
                f"exceed max_input_tokens {policy.max_input_tokens}"
            )

        if (
            policy.max_output_tokens is not None
            and estimate.estimated_output_tokens > policy.max_output_tokens
        ):
            return (
                f"estimated output tokens {estimate.estimated_output_tokens} "
                f"exceed max_output_tokens {policy.max_output_tokens}"
            )

        if (
            policy.max_total_tokens is not None
            and estimate.estimated_total_tokens > policy.max_total_tokens
        ):
            return (
                f"estimated total tokens {estimate.estimated_total_tokens} "
                f"exceed max_total_tokens {policy.max_total_tokens}"
            )

        if (
            policy.max_cost_usd is not None
            and estimate.estimated_total_cost_usd > policy.max_cost_usd
        ):
            return (
                f"estimated total cost {estimate.estimated_total_cost_usd} "
                f"exceed max_cost_usd {policy.max_cost_usd}"
            )

        return None

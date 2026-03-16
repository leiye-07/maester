from __future__ import annotations

from packages.budgets.models import BudgetDecision


class BudgetExceededError(RuntimeError):
    def __init__(self, message: str, *, decision: BudgetDecision) -> None:
        super().__init__(message)
        self.decision = decision

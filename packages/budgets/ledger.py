from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from packages.budgets.models import BudgetEventRecord
from packages.budgets.utils import round_usd, to_decimal


@dataclass(slots=True)
class BudgetLedgerEntry:
    scope_key: str
    request_count: int = 0
    total_cost_usd: Decimal = field(default_factory=lambda: Decimal("0"))

    def as_dict(self) -> dict[str, Any]:
        return {
            "scope_key": self.scope_key,
            "request_count": self.request_count,
            "total_cost_usd": str(round_usd(self.total_cost_usd)),
        }


class InMemoryBudgetLedger:
    def __init__(self) -> None:
        self._entries: dict[str, BudgetLedgerEntry] = {}
        self._events: list[BudgetEventRecord] = []

    def record(self, *,
               scope_key: str,
               actual_cost_usd: Decimal) -> BudgetLedgerEntry:
        entry = self._entries.get(scope_key)
        if entry is None:
            entry = BudgetLedgerEntry(scope_key=scope_key)
            self._entries[scope_key] = entry

        entry.request_count += 1
        entry.total_cost_usd = round_usd(entry.total_cost_usd + 
                                         to_decimal(actual_cost_usd))
        return entry

    def get(self, scope_key: str) -> BudgetLedgerEntry | None:
        return self._entries.get(scope_key)

    def record_event(self, event: BudgetEventRecord) -> None:
        self._events.append(event)

    def list_events(self) -> list[BudgetEventRecord]:
        return list(self._events)

    def list_events_for_scope(self, scope_key: str) -> list[BudgetEventRecord]:
        return [event for event in self._events if event.scope_key == scope_key]

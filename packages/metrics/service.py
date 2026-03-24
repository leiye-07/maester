from collections import defaultdict
from decimal import Decimal

from packages.budgets.models import BudgetEventRecord
from packages.metrics.models import (
    BudgetOutcomeSummary,
    DashboardSummary,
    EstimateAccuracySummary,
    ModelUsageSummary,
    ReliabilityDashboardSnapshot,
    ScopeSpendSummary,
)
from packages.metrics.utils import (normalize_scope_key,
                                    round_usd,
                                    safe_decimal_divide)


class ReliabilityMetricsService:
    def build_snapshot(
        self,
        events: list[BudgetEventRecord],
    ) -> ReliabilityDashboardSnapshot:
        return ReliabilityDashboardSnapshot(
            summary=self._build_summary(events),
            budget_outcomes=self._build_budget_outcomes(events),
            models=self._build_model_usage(events),
            scopes=self._build_scope_spend(events),
            estimate_accuracy=self._build_estimate_accuracy(events),
        )

    def _build_summary(self,
                       events: list[BudgetEventRecord]) -> DashboardSummary:
        total_requests = len(events)
        blocked_requests = sum(1 for e in events if e.decision == "blocked")
        downgraded_requests = sum(1 for e in events
                                  if e.decision == "downgraded")
        allowed_requests = sum(1 for e in events if e.decision == "allowed")
        executed_requests = total_requests - blocked_requests

        total_estimated = round_usd(
            sum((e.estimated_total_cost_usd for e in events), Decimal("0"))
        )
        total_actual = round_usd(
            sum(
                (
                    e.actual_total_cost_usd
                    for e in events
                    if e.actual_total_cost_usd is not None
                ),
                Decimal("0"),
            )
        )

        return DashboardSummary(
            total_requests=total_requests,
            executed_requests=executed_requests,
            blocked_requests=blocked_requests,
            downgraded_requests=downgraded_requests,
            allowed_requests=allowed_requests,
            total_estimated_cost_usd=total_estimated,
            total_actual_cost_usd=total_actual,
            average_estimated_cost_usd=safe_decimal_divide(total_estimated,
                                                           total_requests),
            average_actual_cost_usd=safe_decimal_divide(total_actual,
                                                        executed_requests),
        )

    def _build_budget_outcomes(
        self,
        events: list[BudgetEventRecord],
    ) -> BudgetOutcomeSummary:
        return BudgetOutcomeSummary(
            allowed_count=sum(1 for e in events if e.decision == "allowed"),
            downgraded_count=sum(1 for e in events
                                 if e.decision == "downgraded"),
            blocked_count=sum(1 for e in events if e.decision == "blocked"),
        )

    def _build_model_usage(
        self,
        events: list[BudgetEventRecord],
    ) -> list[ModelUsageSummary]:
        grouped: dict[str, list[BudgetEventRecord]] = defaultdict(list)
        for event in events:
            if event.decision == "blocked":
                continue
            grouped[event.effective_model].append(event)

        summaries: list[ModelUsageSummary] = []
        for model, model_events in grouped.items():
            total_actual = round_usd(
                sum(
                    (
                        e.actual_total_cost_usd
                        for e in model_events
                        if e.actual_total_cost_usd is not None
                    ),
                    Decimal("0"),
                )
            )
            request_count = len(model_events)
            downgrade_count = sum(1 for e in model_events
                                  if e.decision == "downgraded")

            summaries.append(
                ModelUsageSummary(
                    model=model,
                    request_count=request_count,
                    total_actual_cost_usd=total_actual,
                    average_actual_cost_usd=safe_decimal_divide(total_actual,
                                                                request_count),
                    downgrade_count=downgrade_count,
                )
            )

        summaries.sort(key=lambda x: (x.total_actual_cost_usd,
                                      x.request_count), reverse=True)
        return summaries

    def _build_scope_spend(
        self,
        events: list[BudgetEventRecord],
    ) -> list[ScopeSpendSummary]:
        grouped: dict[str, list[BudgetEventRecord]] = defaultdict(list)
        for event in events:
            grouped[normalize_scope_key(event.scope_key)].append(event)

        summaries: list[ScopeSpendSummary] = []
        for scope_key, scope_events in grouped.items():
            request_count = len(scope_events)
            blocked_request_count = sum(1 for e in scope_events
                                        if e.decision == "blocked")
            executed_request_count = request_count - blocked_request_count

            total_estimated = round_usd(
                sum((e.estimated_total_cost_usd for e in scope_events),
                    Decimal("0"))
            )
            total_actual = round_usd(
                sum(
                    (
                        e.actual_total_cost_usd
                        for e in scope_events
                        if e.actual_total_cost_usd is not None
                    ),
                    Decimal("0"),
                )
            )

            summaries.append(
                ScopeSpendSummary(
                    scope_key=scope_key,
                    request_count=request_count,
                    executed_request_count=executed_request_count,
                    blocked_request_count=blocked_request_count,
                    total_estimated_cost_usd=total_estimated,
                    total_actual_cost_usd=total_actual,
                )
            )

        summaries.sort(key=lambda x: (x.total_actual_cost_usd,
                                      x.request_count), reverse=True)
        return summaries

    def _build_estimate_accuracy(
        self,
        events: list[BudgetEventRecord],
    ) -> EstimateAccuracySummary:
        compared = [
            e for e in events
            if e.actual_total_cost_usd is not None
        ]

        compared_request_count = len(compared)
        total_estimated = round_usd(
            sum((e.estimated_total_cost_usd for e in compared), Decimal("0"))
        )
        total_actual = round_usd(
            sum((e.actual_total_cost_usd for e in compared
                 if e.actual_total_cost_usd is not None), Decimal("0"))
        )
        total_abs_delta = round_usd(
            sum(
                (
                    abs(e.estimated_total_cost_usd - e.actual_total_cost_usd)
                    for e in compared
                    if e.actual_total_cost_usd is not None
                ),
                Decimal("0"),
            )
        )

        return EstimateAccuracySummary(
            compared_request_count=compared_request_count,
            average_estimated_cost_usd=safe_decimal_divide(
                total_estimated,
                compared_request_count),
            average_actual_cost_usd=safe_decimal_divide(
                total_actual,
                compared_request_count),
            average_absolute_delta_usd=safe_decimal_divide(
                total_abs_delta,
                compared_request_count),
        )

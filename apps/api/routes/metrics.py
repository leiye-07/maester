from __future__ import annotations

from fastapi import APIRouter, Depends

from apps.api.deps import get_budget_guard
from packages.budgets.service import RequestBudgetGuard
from packages.metrics.models import ReliabilityDashboardSnapshot
from packages.metrics.service import ReliabilityMetricsService

router = APIRouter(tags=["metrics"])


@router.get(
    "/v1/metrics/reliability",
    response_model=ReliabilityDashboardSnapshot,
)
def get_reliability_metrics(
    budget_guard: RequestBudgetGuard = Depends(get_budget_guard),
) -> ReliabilityDashboardSnapshot:
    events = budget_guard.ledger.list_events()
    service = ReliabilityMetricsService()
    return service.build_snapshot(events)

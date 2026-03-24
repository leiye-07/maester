from decimal import Decimal
from pydantic import BaseModel, Field


class DashboardSummary(BaseModel):
    total_requests: int = 0
    executed_requests: int = 0
    blocked_requests: int = 0
    downgraded_requests: int = 0
    allowed_requests: int = 0

    total_estimated_cost_usd: Decimal = Field(default=Decimal("0"))
    total_actual_cost_usd: Decimal = Field(default=Decimal("0"))

    average_estimated_cost_usd: Decimal = Field(default=Decimal("0"))
    average_actual_cost_usd: Decimal = Field(default=Decimal("0"))


class ModelUsageSummary(BaseModel):
    model: str
    request_count: int = 0
    total_actual_cost_usd: Decimal = Field(default=Decimal("0"))
    average_actual_cost_usd: Decimal = Field(default=Decimal("0"))
    downgrade_count: int = 0


class BudgetOutcomeSummary(BaseModel):
    allowed_count: int = 0
    downgraded_count: int = 0
    blocked_count: int = 0


class ScopeSpendSummary(BaseModel):
    scope_key: str
    request_count: int = 0
    executed_request_count: int = 0
    blocked_request_count: int = 0

    total_estimated_cost_usd: Decimal = Field(default=Decimal("0"))
    total_actual_cost_usd: Decimal = Field(default=Decimal("0"))


class EstimateAccuracySummary(BaseModel):
    compared_request_count: int = 0

    average_estimated_cost_usd: Decimal = Field(default=Decimal("0"))
    average_actual_cost_usd: Decimal = Field(default=Decimal("0"))
    average_absolute_delta_usd: Decimal = Field(default=Decimal("0"))


class ReliabilityDashboardSnapshot(BaseModel):
    summary: DashboardSummary
    budget_outcomes: BudgetOutcomeSummary
    models: list[ModelUsageSummary]
    scopes: list[ScopeSpendSummary]
    estimate_accuracy: EstimateAccuracySummary

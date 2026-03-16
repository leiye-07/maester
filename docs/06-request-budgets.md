# Request Budgets

## Why this module exists

One of the fastest ways for an AI product to lose control of spend is to let every request use any model with any token limit.

That is usually acceptable in demos.
It becomes dangerous in production.

A single expensive route can create three problems at once:

- runaway token usage
- incorrect model selection for low-value work
- delayed visibility into spend because cost is only measured after the call finishes

Maester introduces **request budgets** as the first enforceable cost-control primitive in the reliability stack.

## What request budgets do

Request budgets apply a **pre-flight policy check** before a model call is dispatched.

For each request, Maester can:

1. estimate the worst-case cost
2. compare it against policy
3. allow the request, downgrade it to a cheaper model, or reject it early
4. record the actual spend after the response returns

This creates a simple but useful control loop:

```text
request
  ↓
estimate cost
  ↓
policy check
  ├─ allow
  ├─ fallback to cheaper model
  └─ reject early
  ↓
model gateway
  ↓
cost metering
  ↓
ledger update
```

## Current scope

The first version is intentionally small.

### Inputs used for estimation

- prompt length
- requested model
- `max_tokens`
- static model pricing

### Current controls

- `max_cost_usd`
- `max_input_tokens`
- `max_output_tokens`
- `max_total_tokens`
- optional `fallback_model_if_over_budget`

### Current outcomes

- **allowed**: request proceeds as requested
- **fallback**: request is re-routed to a cheaper model if policy allows
- **blocked**: request fails before provider dispatch

## Why estimation happens before the call

Metering actual spend is necessary, but it is not enough.

If cost is only measured after provider execution, the expensive request has already happened.

Request budgets move one important decision earlier:

> should this request run at all, and should it run on this model?

This is why the module sits before the model gateway call, while the existing cost meter remains after execution.

## Current estimation strategy

The implementation uses a simple deterministic estimate:

- input tokens ≈ `ceil(len(prompt) / 4)`
- output tokens = requested `max_tokens`

This is intentionally conservative and easy to explain.

It is not designed to be a perfect tokenizer.
It is designed to be a practical pre-flight control.

## API behavior

`/v1/reliable_completion` now supports these budget fields:

- `budget_scope`
- `max_cost_usd`
- `allow_fallback_to_cheaper_model`

When a request budget is active, the response includes:

- budget policy
- estimate
- effective model
- whether fallback was applied
- actual total cost
- in-memory ledger totals for the scope

## Example scenarios

### 1. Within budget

A request for `gpt-4.1-mini` with a modest token ceiling passes the pre-flight check and executes normally.

### 2. Downgraded to a cheaper model

A request for `gpt-4.1` exceeds the cost limit, but the configured fallback model (`gpt-4.1-mini`) fits within policy.
The request is downgraded automatically.

### 3. Blocked before dispatch

A request exceeds the allowed cost and the fallback model still does not fit.
The request is rejected before any provider call is made.

## Why this matters for reliability

Cost control is not only a finance concern.
It is also a reliability concern.

Systems become harder to operate when:

- spend is unpredictable
- expensive paths are invisible
- model selection is inconsistent
- budget failures are discovered too late

Request budgets create a predictable control point in the request lifecycle.

## What this does **not** do yet

This module does not yet handle:

- monthly tenant budgets
- async batch job policies
- prompt caching policy
- eval-aware routing
- anomaly detection
- invoice-grade billing

Those belong to later layers of the cost optimization stack.

## Where this fits in Maester

Request budgets are the first hard control in a larger cost architecture:

```text
request shaping
  ↓
request budgets
  ↓
runtime metering
  ↓
visibility and dashboards
  ↓
advanced optimization
```

That makes this module a good foundation for future work such as:

- request budget dashboards
- scope-level monthly caps
- cost-aware model routing
- cache-aware policy decisions
- quality/cost optimization loops

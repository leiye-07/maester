# Cost Model
AI APIs introduce a unique operational concern: **token economics**.

Unlike traditional APIs, every request has a direct cost associated with it.

This document explains how cost accounting is implemented for:

- model inference
- embeddings
- background jobs
---

## Why Cost Visibility Matters

When running AI APIs, teams must understand:

- which requests consume the most tokens
- which models are the most expensive
- how usage affects system economics

Without visibility, it becomes difficult to:

- control spending
- debug runaway prompts
- plan capacity

Cost therefore becomes part of reliability.

---

## Token-Based Pricing

Most AI providers charge based on token usage.

Typical pricing components:

- input tokens
- output tokens
- model-specific rates

Example pricing structure:
> Model: gpt-4o-mini <br>
Input tokens: $0.00015 / 1k tokens <br>
Output tokens: $0.00060 / 1k tokens


Maester stores these values in a pricing catalog.

---

## Pricing Catalog

The pricing catalog maps model names to their costs.

Example structure:

```python
MODEL_PRICING = {
    "gpt-4o-mini": {
        "input_per_1k": 0.00015,
        "output_per_1k": 0.00060,
    }
}
```
This allows cost calculation to remain deterministic.

## Cost Calculation

Given:
> input_tokens = 800
<br>output_tokens = 300

The calculation becomes:
>input_cost = (input_tokens / 1000) * input_price
<br>output_cost = (output_tokens / 1000) * output_price
<br>total_cost = input_cost + output_cost

The result is recorded for the request.

Example Output

A request might produce the following cost record:
```json
{
  "model": "gpt-4o-mini",
  "input_tokens": 800,
  "output_tokens": 300,
  "total_cost_usd": 0.00027
}
```

This information can later be used for:
- debugging
- cost dashboards
- request analysis
- usage reporting

## Future Extensions
Possible extensions to the cost model include:
- multi-provider pricing
- cached prompt discounts
- request-level cost budgets
- usage aggregation
- cost anomaly detection

These features are outside the scope of the initial toolkit but are compatible with the current architecture.
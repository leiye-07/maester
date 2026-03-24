# Reliability Dashboard

## Purpose

This dashboard exposes a backend-first summary of:
- actual spend
- estimated spend
- model usage
- budget outcomes
- estimate accuracy

## Data source

The dashboard is built from `BudgetEventRecord` events emitted during request execution.

## Why API-first

The dashboard is currently exposed as a JSON API instead of a UI to keep the implementation small and reusable.

## Endpoint

`GET /v1/metrics/reliability`

## Snapshot fields

- summary
- budget_outcomes
- models
- scopes
- estimate_accuracy

## Demo

Run:

```bash
bash packages/testing/scenarios/reliability_metrics_scenarios.sh
```
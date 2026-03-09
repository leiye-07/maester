# 02 — Design Decisions

This document records the key architectural decisions behind Maester.

The goal is not perfection, but transparency.

---

## Decision 1 — Lightweight Tracing Instead of Full Telemetry

The tracing system is intentionally minimal.

It provides:

- trace IDs
- span timing
- structured span logs

It does not implement:

- distributed tracing
- collectors
- exporters
- telemetry pipelines

These responsibilities belong to systems such as OpenTelemetry.

Maester focuses on **application-layer visibility**.

---

## Decision 2 — Cost as a First-Class Runtime Signal

Traditional APIs measure:

- latency
- error rate

AI systems must also measure:

- **economic cost**

Because token usage directly affects system economics.

Maester therefore includes:

- model pricing catalog
- token usage accounting
- request-level cost estimation

Cost is treated as a **runtime metric**, not just a billing concern.

---

## Decision 3 — Evaluation as Part of Runtime Flow

AI outputs are probabilistic.

A successful API call does not guarantee a correct result.

Therefore evaluation logic is included directly in the request flow.

Current checks are simple:

- non-empty response
- required term presence
- length validation

The architecture allows richer evaluation later.

---

## Decision 4 — Introduce a Model Gateway Layer

AI systems rarely stay bound to a single provider.

Over time, teams often need to support:

- multiple vendors
- model-specific routing
- fallback behavior
- provider experimentation

Embedding provider logic directly inside route handlers creates tight coupling and makes reliability harder to manage. Therefore a Model gateway layer is introduced.

**Why this matters**

This decision improves:

- provider portability
- system clarity
- fallback reliability
- future extensibility

This keeps the API layer simple while moving provider-specific behavior into infrastructure modules.
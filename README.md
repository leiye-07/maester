# Maester — AI Reliability Toolkit

Production infrastructure for building **reliable, cost-aware AI systems**.

Maester provides the missing layer between:
- raw LLM APIs
- production-grade AI applications

It turns fragile AI demos into **controlled, observable, and budget-safe systems**.

---

## Why Maester

Most AI systems break after the demo stage:

- Costs explode unpredictably
- Prompts drift without version control
- Debugging becomes impossible
- Model routing is ad-hoc
- No guardrails exist for real-world usage

Maester introduces **engineering discipline to AI systems**:
- request-level cost control
- reproducibility
- observability
- evaluation
- reliability metrics

---

## Core Capabilities

### 1. Reliable Completion API
Wrap LLM calls with:
- request replay
- prompt versioning
- structured execution

```bash
POST /v1/reliable_completion
```


---

### 2. Request Budgets (Cost Guardrails)

Every request is evaluated before execution:

- estimate cost upfront
- enforce max budget
- optionally downgrade to cheaper models
- block unsafe requests

Decision types:
- `allowed`
- `downgraded`
- `blocked`

This prevents:
- runaway token usage
- unexpected API bills
- unbounded agent behavior

---
### 3. Budget Event Ledger

Each request produces a structured event:

- estimated vs actual cost
- model used (requested vs effective)
- decision outcome
- scope attribution

This enables:
- cost visibility
- system-level accountability
- downstream analytics

---
### 4. Reliability Metrics API

Maester exposes a backend-first dashboard:

```bash
GET /v1/metrics/reliability
```

Returns:

- total spend (estimated vs actual)
- budget outcomes (allowed / downgraded / blocked)
- model usage distribution
- cost by scope
- estimate accuracy

Example:

```json
{
  "summary": {
    "total_requests": 3,
    "executed_requests": 2,
    "blocked_requests": 1
  },
  "models": [
    {
      "model": "gpt-4.1-mini",
      "request_count": 2
    }
  ]
}
```
---

### 5. Model Gateway

Abstracts model providers:
- multi-model routing
- cost-aware selection
- future support for multi-provider setups

---

### 6. Observability

Built-in:
- structured logging
- tracing hooks

Designed for:
- production debugging
- system introspection

---
### 7. Prompt Registry

Treat prompts as code:
- versioning
- reuse
- controlled evolution
---

### 8. Request Replay (Debugging)

Reproduce failures deterministically:

replay historical requests
compare outputs
debug regressions

---
## Architecture
```
Client
  ↓
Reliable Completion API
  ↓
Request Budget Guard
  ↓
Model Gateway
  ↓
LLM Provider
  ↓
Event Ledger
  ↓
Metrics API
```

Key idea:
> Every AI request becomes a tracked, measurable, and controllable unit of execution.

---
## Repository Structure
```
maester/
├── apps/
│   ├── api/            # FastAPI service
│   └── worker/         # async jobs
│
├── packages/
│   ├── common/         # shared infra
│   ├── observability/  # logging / tracing
│   ├── model_gateway/  # LLM abstraction
│   ├── prompt_registry/
│   ├── evaluation/
│   ├── replay/
│   ├── budgets/        # request budgets + ledger
│   └── metrics/        # reliability dashboard
│
├── infra/
│   └── docker-compose.yml
│
├── tests/              # bash test scripts
|
└── docs/
```
---

## Quick Start
### 1. Start the service
```bash
docker-compose up
```
or:
```bash
uvicorn apps.api.main:app --reload
```

### 2. Send a request

```bash
curl http://localhost:8000/v1/reliable_completion \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain vector databases",
    "model": "gpt-4.1",
    "max_tokens": 300,
    "max_cost_usd": "0.01",
    "budget_scope": "demo"
  }'
```
---

### 3. Inspect reliability metrics
```bash
curl http://localhost:8000/v1/metrics/reliability
```
---

### 4. Run full scenario
```bash
bash packages/testing/scenarios/reliability_metrics_scenarios.sh
```

---
## Design Principles
### 1. Budget Before Execution

Every request must pass a cost check before hitting the model.

---
### 2. Events Over Logs

AI systems should produce structured events, not just logs.

---
### 3. Reproducibility First

If you can't replay it, you can't debug it.

---
### 4. API-First Observability

Metrics are exposed as APIs, not dashboards.

---
### 5. Production > Demo

The goal is not to generate text —
the goal is to operate AI systems reliably.

---
## Roadmap
- multi-provider routing (OpenAI / Anthropic / local)
- persistent event store
- real-time dashboards
- evaluation pipelines
- policy-based routing
- enterprise cost controls

---
## Positioning

Maester is not:
- a chatbot framework
- a prompt library
- a wrapper around OpenAI

Maester is:

> Infrastructure for AI reliability and cost control in production systems

----
## Author

Built as part of the Notrix AI Infrastructure initiative.

Focus:
- AI reliability
- production ML systems
- cost-aware AI architectures
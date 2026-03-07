# maester

## AI Reliability Toolkit

Maester is a minimal AI infrastructure skeleton focused on **reliable AI APIs**.

It demonstrates four reliability primitives:

- **Observability** — structured logs and lightweight tracing
- **Cost Metering** — token and cost accounting per request
- **Evaluation** — basic response quality checks
- **Separation of Concerns** — API, worker, gateway, and shared packages

Maester is designed as a teaching artifact and authority repo for production-minded AI systems.

---

## Quick Start
### Run API

From the repo root:
```bash
uvicorn apps.api.main:app --reload
```
Then open:

http://localhost:8000/docs

### Run Worker
```bash
python apps/worker/worker.py
```

### Run with Docker Compose

From infra/:
```bash
docker compose up
```

Example API Request
```bash
curl -X POST http://localhost:8000/v1/reliable_completion \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Summarize why reliable AI APIs need observability, cost tracking, and evaluation.",
    "model": "gpt-4.1-mini",
    "required_terms": ["observability", "evaluation"],
    "max_response_chars": 400
  }'
```

Example Response
```bash
{
  "model": "gpt-4.1-mini",
  "content": "Maester response: processed prompt 'Summarize why reliable AI APIs need observability, cost tracking, and evaluation.' with reliability instrumentation enabled.",
  "trace_id": "9b3f0f6b6f1a4c8d8d5f3b9aef8d4f25",
  "cost": {
    "model": "gpt-4.1-mini",
    "input_tokens": 20,
    "output_tokens": 20,
    "total_tokens": 40,
    "input_cost_usd": "0.000008",
    "output_cost_usd": "0.000032",
    "total_cost_usd": "0.000040",
    "unit": "USD"
  },
  "evaluation": {
    "status": "pass",
    "reliability_score": 1.0,
    "metrics": [
      {
        "name": "non_empty",
        "score": 1.0,
        "passed": true,
        "reason": null
      }
    ]
  }
}
```
#!/usr/bin/env bash
set -euo pipefail

BASE_URL="http://localhost:8000"

echo "1) allowed request"
curl -s "$BASE_URL/v1/reliable_completion" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain vector databases simply.",
    "model": "gpt-4.1-mini",
    "max_tokens": 150,
    "max_cost_usd": "0.01",
    "budget_scope": "demo"
  }' | jq .

echo
echo "2) downgraded request"
curl -s "$BASE_URL/v1/reliable_completion" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain transformers architecture in detail.",
    "model": "gpt-4.1",
    "max_tokens": 600,
    "max_cost_usd": "0.001",
    "budget_scope": "demo",
    "allow_fallback_to_cheaper_model": true
  }' | jq .

echo
echo "3) blocked request"
curl -s "$BASE_URL/v1/reliable_completion" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a long explanation of reinforcement learning.",
    "model": "gpt-4.1",
    "max_tokens": 1200,
    "max_cost_usd": "0.00001",
    "budget_scope": "demo",
    "allow_fallback_to_cheaper_model": false
  }' | jq .

echo
echo "4) dashboard snapshot"
curl -s "$BASE_URL/v1/metrics/reliability" | jq .

#!/usr/bin/env bash

BASE_URL="http://localhost:8000/v1/reliable_completion"

echo "Scenario 1: request allowed within budget"

curl -s $BASE_URL \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain vector databases in simple terms.",
    "model": "gpt-4.1-mini",
    "max_tokens": 200,
    "max_cost_usd": "0.01"
  }' | jq .

echo ""
echo "Scenario 2: downgrade expensive model to cheaper fallback"

curl -s $BASE_URL \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain transformers architecture in detail.",
    "model": "gpt-4.1",
    "max_tokens": 500,
    "max_cost_usd": "0.001",
    "allow_fallback_to_cheaper_model": true
  }' | jq .

echo ""
echo "Scenario 3: request blocked by budget"

curl -s $BASE_URL \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a long explanation of reinforcement learning.",
    "model": "gpt-4.1",
    "max_tokens": 1000,
    "max_cost_usd": "0.00001",
    "allow_fallback_to_cheaper_model": false
  }' | jq .
#!/usr/bin/env bash
set -euo pipefail

BASE_URL="http://localhost:8000/v1/prompted_completion"

echo "Scenario 1: prompted completion with explicit version"

curl -s "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_name": "system_summary",
    "prompt_version": "v1",
    "variables": {
      "event_text": "Admin revoked API key for user account 742."
    },
    "model": "gpt-4.1-mini",
    "max_tokens": 120
  }' | jq .

echo
echo "Scenario 2: prompted completion with default version"

curl -s "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_name": "system_summary",
    "variables": {
      "event_text": "System latency increased above 300ms for the inference service."
    }
  }' | jq .

echo
echo "Scenario 3: prompted completion with explicit model"

curl -s "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_name": "system_summary",
    "variables": {
      "event_text": "Admin revoked API key for user account 142."
    },
    "model": "gpt-4.1-mini",
    "max_tokens": 120
  }' | jq .

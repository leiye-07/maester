#!/usr/bin/env bash
set -euo pipefail

BASE_URL="http://localhost:8000/v1/reliable_completion"

echo "Scenario 1: reliable completion with required terms"

curl -s "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Summarize the system health and mention healthy and passed",
    "model": "gpt-4.1-mini",
    "max_tokens": 150,
    "required_terms": ["healthy", "passed"],
    "max_response_chars": 300
  }' | jq .

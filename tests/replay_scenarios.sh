#!/usr/bin/env bash
set -euo pipefail

BASE_URL="http://localhost:8000"

echo "Scenario 1: create replayable prompted completion"

response=$(curl -s "$BASE_URL/v1/prompted_completion" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_name": "system_summary",
    "prompt_version": "v1",
    "variables": {
      "event_text": "Admin revoked API key for user account 742."
    },
    "model": "gpt-4.1-mini",
    "max_tokens": 120
  }')

printf '%s\n' "$response" | jq .

request_id=$(printf '%s\n' "$response" | jq -r '.request_id')

echo
echo "Scenario 2: fetch replay record"

curl -s "$BASE_URL/v1/replays/$request_id" | jq .

echo
echo "Scenario 3: run replay"

curl -s -X POST "$BASE_URL/v1/replays/$request_id/run" | jq .

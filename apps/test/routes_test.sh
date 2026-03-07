
curl -X POST http://localhost:8000/v1/reliable_completion \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Summarize the system health and mention healthy and passed",
    "model": "gpt-4.1-mini",
    "required_terms": ["healthy", "passed"],
    "max_response_chars": 300
  }'
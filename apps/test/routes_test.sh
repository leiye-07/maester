
curl -X POST http://localhost:8000/v1/reliable_completion \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Summarize the system health and mention healthy and passed",
    "model": "gpt-4.1-mini",
    "max_tokens": 150,
    "required_terms": ["healthy", "passed"],
    "max_response_chars": 300
  }'


  curl -X POST http://localhost:8000/v1/prompted_completion \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_name": "system_summary",
    "prompt_version": "v1",
    "variables": {
      "event_text": "Admin revoked API key for user account 742."
    },
    "model": "gpt-4.1-mini",
    "max_tokens": 120
  }'


  curl -X POST http://localhost:8000/v1/prompted_completion \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_name": "system_summary",
    "variables": {
      "event_text": "System latency increased above 300ms for the inference service."
    }
  }'


curl -X POST http://localhost:8000/v1/prompted_completion \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_name": "system_summary",
    "variables": {
      "event_text": "Admin revoked API key for user account 142."
    },
    "model": "gpt-4.1-mini",
    "max_tokens": 120
  }'


## replay record
curl http://localhost:8000/v1/replays/$request_id

## run replay
curl -X POST http://localhost:8000/v1/replays/$request_id/run



# Request Replay

AI systems behave differently from traditional deterministic software.

The same prompt sent to the same model may produce different responses over time due to:

- model updates
- temperature randomness
- provider infrastructure changes
- prompt version changes
- dependency updates

Because of this, reproducing historical responses becomes difficult.

Request Replay is designed to solve this problem.

## Why Replay Matters

In production AI systems, teams frequently encounter questions like:
- Why did the model produce this answer?
- Why does the system behave differently today?
- Did a prompt update introduce regression?
- Did a provider change model behavior?

Without replay capability, these questions are extremely difficult to answer.

Replay allows engineers to:
- reproduce past AI requests
- compare outputs across model versions
- debug prompt changes
- convert incidents into test fixtures

Replay therefore becomes part of AI system observability.

## Replay Record

Each AI request produces a replay record.

This record captures the minimal information required to reproduce the request. The replay record stores:
- prompt identity
- prompt variables
- model selection
- provider information
- model response
- evaluation result
- cost accounting

This information allows the request to be executed again later.

## Replay Architecture

Replay is implemented as separate subsystem.
```txt
API Request
   ↓
Prompt Registry
   ↓
Model Gateway
   ↓
Evaluation + Cost Meter
   ↓
Replay Recorder (+)
   ↓
Replay Store (+)
```
When a request finishes, the replay recorder builds a structured record and saves it to the replay store.

Later, the replay system can re-run the request.
```txt
Replay Request (+)
   ↓
Replay Store (+)
   ↓
Model Gateway
   ↓
Evaluation
   ↓
Comparison Engine (+)
```

## Replay Execution

Replaying a request means executing the same prompt again.

Example replay flow:

1. Retrieve replay record from storage
2. Reconstruct the rendered prompt
3. Send the prompt through the model gateway
4. Run evaluation again
5. Compare outputs

## Converting Replays into Tests

Replay artifacts can be converted into test fixtures.

This allows production incidents to become reproducible.
```txt
production request
    ↓
replay record (+)
    ↓
test fixture (+)
    ↓
evaluation suite
```

## Future Extensions

Replay systems can be extended with:
- multi-provider replay comparison
- prompt version drift analysis
- evaluation regression alerts
- dataset generation for evaluation suites
- automated replay pipelines

These features are outside the scope of the initial toolkit but align with the current architecture.
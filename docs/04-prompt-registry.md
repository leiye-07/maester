# Prompt Registry

AI systems often evolve through prompt iteration.

Small prompt changes can significantly affect model behavior, evaluation results, and downstream application logic.

Without version tracking, prompt changes become difficult to **reproduce** or **debug**.

This document explains how prompt management is implemented in Maester through a **Prompt Registry**.

The registry provides:
- Versioned prompt templates
- Deterministic prompt rendering
- Prompt hashing for traceability


## Why Prompt Versioning Matters

During early development, prompts are often embedded directly in application code:
```python
prompt = f"Summarize the following system event:\n\n{event_text}"
```
While convenient, this approach introduces several operational risks.

Teams may struggle to understand:
- Which prompt version produced a response
- Whether a prompt changed between deployments
- How prompt changes affect evaluation metrics

Without version control, prompt behavior may drift silently. Prompt management therefore becomes part of system reliability.

## Prompt Templates

Maester defines prompts as structured templates.

Each template contains:
- name
- version
- template content

Example prompt definition:
```python
PromptTemplate(
    name="system_summary",
    version="v2",
    template=(
        "You are a production AI assistant focused on reliability.\n"
        "Summarize the following system event.\n\n"
        "{event_text}"
    ),
)
```
Prompt templates are registered inside the Prompt Registry.

## Prompt Rendering

Prompts are rendered using the PromptService.

Example usage:
```python
rendered = prompt_service.render(
    name="system_summary",
    variables={
        "event_text": "User downloaded a large dataset."
    }
)
```
The registry resolves the appropriate template version and renders the final prompt.

## Version Resolution

Prompt versions can be resolved in two ways.

**1. Latest Version**

If a version is not specified, the registry returns the most recent template.

Example request:
```python
prompt_service.render(
    name="system_summary",
    variables={"event_text": "..."}
)
```
**2. Explicit Version**

A specific version can also be requested.
```python
prompt_service.render(
    name="system_summary",
    version="v1",
    variables={"event_text": "..."}
)
```
Explicit versioning is recommended for:
- Evaluation benchmarks
- Regression testing
- Reproducible experiments

## Future Extensions

Possible extensions to the prompt registry include:
- Database-backed prompt storage
- Prompt experiment tracking
- Prompt A/B testing
- Evaluation-linked prompt selection
- pPrompt rollout policies
These features are currently outside the scope of the initial toolkit but are compatible with the current architecture.
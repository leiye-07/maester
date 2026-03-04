"""
Dependency injection helpers for FastAPI routes.

Responsibilities:
- Provide tenant context
- Provide database connections
- Provide authenticated request context

Future additions:
- tenant resolution via API key
- usage metering injection
- request-scoped tracing context
"""
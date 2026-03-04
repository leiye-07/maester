"""
FastAPI application entrypoint.

Responsibilities:
- Initialize API application
- Attach middleware (request id, auth, logging)
- Register route modules
- Provide health and readiness endpoints

Future extensions:
- Tenant API key authentication
- Rate limiting
- Request tracing propagation
"""

from fastapi import FastAPI
from apps.api.routes.health import router as health_router

app = FastAPI(title="B2B AI SaaS Infra Blueprint")

app.include_router(health_router)

@app.get("/")
def root():
    return {"service": "b2b-ai-saas-infra-blueprint", "status": "running"}
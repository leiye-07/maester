"""
Health check endpoints.

Used by:
- load balancers
- container orchestrators
- uptime monitors
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "healthy"}
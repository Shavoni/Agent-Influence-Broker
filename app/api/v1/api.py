"""
Agent Influence Broker - Main API Router

Integrates all API endpoints following FastAPI best practices
with comprehensive routing and documentation.
"""

from fastapi import APIRouter

from app.core.logging import get_logger

logger = get_logger(__name__)

# Main API router
router = APIRouter()

# Health check endpoints


@router.get("/health", tags=["System"])
async def system_health():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "service": "Agent Influence Broker API",
        "version": "1.0.0",
    }


@router.get("/version", tags=["System"])
async def api_version():
    """API version information."""
    return {
        "version": "1.0.0",
        "api_version": "v1",
        "features": ["agent_management", "negotiations", "transactions"],
    }

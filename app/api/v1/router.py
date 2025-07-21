"""Main API router for version 1."""

from fastapi import APIRouter

from app.api.v1.endpoints import agents, influence, negotiations, transactions

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])

api_router.include_router(
    negotiations.router, prefix="/negotiations", tags=["negotiations"]
)

api_router.include_router(
    transactions.router, prefix="/transactions", tags=["transactions"]
)

api_router.include_router(
    influence.router, prefix="/influence", tags=["influence"]
)


@api_router.get("/status")
async def api_status():
    """API status endpoint."""
    return {"status": "API v1 is operational", "endpoints": "coming soon"}

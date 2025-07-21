"""
Agent Influence Broker - Influence API Routes

Influence metrics and analytics endpoints for agent performance tracking.
"""


from fastapi import APIRouter, Depends, Query

from app.core.logging import get_logger
from app.core.security import get_current_user_token
from app.schemas.influence import AgentInfluenceScore, InfluenceMetricsResponse
from app.services.influence_service import influence_service

logger = get_logger(__name__)

router = APIRouter()


@router.get("/agent/{agent_id}", response_model=AgentInfluenceScore)
async def get_agent_influence_score(
    agent_id: str,
    time_window_days: int = Query(30, ge=1, le=365),
    current_user=Depends(get_current_user_token),
):
    """Get agent influence score with breakdown."""
    return await influence_service.calculate_agent_influence_score(
        agent_id, time_window_days
    )


@router.get("/metrics/{agent_id}", response_model=InfluenceMetricsResponse)
async def get_influence_metrics(
    agent_id: str, current_user=Depends(get_current_user_token)
):
    """Get comprehensive influence metrics for agent."""
    return await influence_service.get_influence_metrics(agent_id)

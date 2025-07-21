"""
Agent API routes
"""

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db_session
from ..core.security import get_current_active_user, require_user
from ..schemas.agents import (
    AgentCreate,
    AgentListResponse,
    AgentResponse,
    AgentSearchFilters,
    AgentService,
    AgentStats,
    AgentSummary,
    AgentUpdate,
    APIRouter,
    ..core.exceptions,
    ..services.agent_service,
    :,
    =,
    agent_not_found_http,
    from,
    import,
    router,
)


@router.post(
    "/",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED
):
async def create_agent(
    agent_data: AgentCreate,
    current_user: dict = Depends(require_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new agent"""
    agent_service = AgentService(db)
    agent = await agent_service.create_agent(
        agent_data,
        current_user["user_id"]
    )
    return agent


@router.get(
    "/",
    response_model=AgentListResponse
)
async def list_agents(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    agent_type: Optional[str] = Query(
        None, description="Filter by agent type"
    ),
    is_active: Optional[bool] = Query(
        None, description="Filter by active status"
    ),
    is_verified: Optional[bool] = Query(
        None, description="Filter by verified status"
    ),
    min_reputation: Optional[float] = Query(
        None, ge=0, le=100, description="Minimum reputation score"
    ),
    db: AsyncSession = Depends(get_db_session)
) -> AgentListResponse:
    """List agents with optional filtering"""

    filters = AgentSearchFilters(
        agent_type=agent_type,
        is_active=is_active,
        is_verified=is_verified,
        min_reputation=min_reputation
    )

    agent_service = AgentService(db)
    result = await agent_service.list_agents(
        page=page,
        size=size,
        filters=filters
    )
    return result

list_agents.__annotations__["return"] = AgentListResponse


@router.get(
    "/my",
    response_model=List[AgentSummary]
)
async def get_my_agents(
    current_user: dict = Depends(require_user),
    db: AsyncSession = Depends(get_db_session)
) -> List[AgentSummary]:
    """Get current user's agents"""
    agent_service = AgentService(db)
    agents = await agent_service.get_agents_by_owner(current_user["user_id"])
    return agents

get_my_agents.__annotations__["return"] = List[AgentSummary]


@router.get(
    "/{agent_id}",
    response_model=AgentResponse
)
async def get_agent(
    agent_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Get agent by ID"""
    agent_service = AgentService(db)
    agent = await agent_service.get_agent_by_id(agent_id)

    if not agent:
        raise agent_not_found_http(str(agent_id))

    return agent


@router.put(
    "/{agent_id}",
    response_model=AgentResponse
)
async def update_agent(
    agent_id: uuid.UUID,
    agent_data: AgentUpdate,
    current_user: dict = Depends(require_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Update agent"""
    agent_service = AgentService(db)

    # Check ownership
    agent = await agent_service.get_agent_by_id(agent_id)
    if not agent:
        raise agent_not_found_http(str(agent_id))

    if agent.owner_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this agent"
        )

    updated_agent = await agent_service.update_agent(agent_id, agent_data)
    return updated_agent


@router.delete(
    "/{agent_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_agent(
    agent_id: uuid.UUID,
    current_user: dict = Depends(require_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Delete agent (soft delete - deactivate)"""
    agent_service = AgentService(db)

    # Check ownership
    agent = await agent_service.get_agent_by_id(agent_id)
    if not agent:
        raise agent_not_found_http(str(agent_id))

    if agent.owner_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this agent"
        )

    await agent_service.deactivate_agent(agent_id)


@router.get(
    "/{agent_id}/stats",
    response_model=AgentStats
)
async def get_agent_stats(
    agent_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Get agent statistics"""
    agent_service = AgentService(db)
    agent = await agent_service.get_agent_by_id(agent_id)

    if not agent:
        raise agent_not_found_http(str(agent_id))

    stats = await agent_service.get_agent_stats(agent_id)
    return stats


@router.post("/{agent_id}/verify")
async def verify_agent(
    agent_id: uuid.UUID,
    current_user: dict = Depends(
        require_user
    ),  # In reality, this would be admin only
    db: AsyncSession = Depends(get_db_session)
):
    """Verify an agent (admin only in production)"""
    agent_service = AgentService(db)
    agent = await agent_service.get_agent_by_id(agent_id)

    if not agent:
        raise agent_not_found_http(str(agent_id))

    await agent_service.verify_agent(agent_id)
    return {"message": "Agent verified successfully"}


@router.post("/{agent_id}/activate")
async def activate_agent(
    agent_id: uuid.UUID,
    current_user: dict = Depends(require_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Activate an agent"""
    agent_service = AgentService(db)
    agent = await agent_service.get_agent_by_id(agent_id)

    if not agent:
        raise agent_not_found_http(str(agent_id))

    if agent.owner_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to activate this agent"
        )

    await agent_service.activate_agent(agent_id)
    return {"message": "Agent activated successfully"}

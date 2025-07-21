"""Agent management API endpoints with comprehensive authentication and validation."""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from app.core.auth import User, get_mock_user, verify_agent_ownership
from app.core.config import get_settings
from app.core.exceptions import (
    BusinessLogicError,
    NotFoundError,
    ValidationError,
)
from app.schemas.agent import (
    AgentCreateRequest,
    AgentResponse,
    AgentUpdateRequest,
)
from app.services.agent_service import AgentService

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_agent_service() -> AgentService:
    """Dependency to get agent service instance."""
    return AgentService()


async def get_current_user_dependency() -> User:
    """
    Get current user with environment-based authentication.

    In development, uses mock user. In production, uses JWT authentication.
    """
    settings = get_settings()

    if settings.ENVIRONMENT == "development":
        return await get_mock_user()
    else:
        # In production, this would use get_current_active_user
        return (
            await get_mock_user()
        )  # Replace with get_current_active_user for production


@router.post(
    "/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED
)
async def create_agent(
    agent_data: AgentCreateRequest,
    agent_service: AgentService = Depends(get_agent_service),
    current_user: User = Depends(get_current_user_dependency),
) -> AgentResponse:
    """
    Create a new AI agent.

    Args:
        agent_data: Agent creation data with validation
        agent_service: Agent service dependency
        current_user: Authenticated user

    Returns:
        Created agent instance with full metadata

    Raises:
        HTTPException: If creation fails due to validation or business logic errors
    """
    try:
        logger.info(
            f"Creating agent for user {current_user.id}: {agent_data.name}"
        )

        created_agent = await agent_service.create_agent(
            agent_data, current_user.id
        )

        logger.info(
            f"Agent created successfully: {created_agent.id} "
            f"by user {current_user.id}"
        )
        return created_agent

    except ValidationError as e:
        logger.warning(
            f"Agent creation validation error for user {current_user.id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": "Validation failed", "message": str(e)},
        )
    except BusinessLogicError as e:
        logger.warning(
            f"Agent creation business logic error for user {current_user.id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Business logic violation", "message": str(e)},
        )
    except Exception as e:
        logger.error(
            f"Unexpected error creating agent for user {current_user.id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    agent_service: AgentService = Depends(get_agent_service),
    current_user: User = Depends(get_current_user_dependency),
) -> AgentResponse:
    """
    Retrieve an agent by ID with ownership verification.

    Args:
        agent_id: Agent identifier
        agent_service: Agent service dependency
        current_user: Authenticated user

    Returns:
        Agent instance with all metadata

    Raises:
        HTTPException: If agent not found or access denied
    """
    try:
        logger.info(f"User {current_user.id} requesting agent {agent_id}")

        agent = await agent_service.get_agent_by_id(agent_id, current_user.id)

        # Verify access permissions
        if (
            not verify_agent_ownership(agent_id, current_user)
            and agent.status != "active"
        ):
            logger.warning(
                f"Access denied: user {current_user.id} for agent {agent_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )

        return agent

    except NotFoundError as e:
        logger.warning(
            f"Agent not found: {agent_id} for user {current_user.id}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Not found", "message": str(e)},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    skip: int = Query(
        0, ge=0, description="Number of agents to skip for pagination"
    ),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of agents to return"
    ),
    status: Optional[str] = Query(None, description="Filter by agent status"),
    owner_only: bool = Query(False, description="Show only user's own agents"),
    agent_service: AgentService = Depends(get_agent_service),
    current_user: User = Depends(get_current_user_dependency),
) -> List[AgentResponse]:
    """
    List agents with pagination, filtering, and access control.

    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        status: Optional status filter (active, inactive, suspended)
        owner_only: If true, show only user's own agents
        agent_service: Agent service dependency
        current_user: Authenticated user

    Returns:
        List of agents accessible to the user
    """
    try:
        logger.info(
            f"User {current_user.id} listing agents: "
            f"skip={skip}, limit={limit}, status={status}, owner_only={owner_only}"
        )

        # Apply ownership filter based on user preference
        user_id_filter = current_user.id if owner_only else None

        agents = await agent_service.list_agents(
            user_id=user_id_filter,
            skip=skip,
            limit=limit,
            status_filter=status,
        )

        logger.info(
            f"Returned {len(agents)} agents for user {current_user.id}"
        )
        return agents

    except Exception as e:
        logger.error(
            f"Unexpected error listing agents for user {current_user.id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    update_data: AgentUpdateRequest,
    agent_service: AgentService = Depends(get_agent_service),
    current_user: User = Depends(get_current_user_dependency),
) -> AgentResponse:
    """
    Update an existing agent with ownership verification.

    Args:
        agent_id: Agent identifier
        update_data: Agent update data with validation
        agent_service: Agent service dependency
        current_user: Authenticated user

    Returns:
        Updated agent instance

    Raises:
        HTTPException: If update fails or access denied
    """
    try:
        logger.info(f"User {current_user.id} updating agent {agent_id}")

        # Verify ownership before attempting update
        if not verify_agent_ownership(agent_id, current_user):
            logger.warning(
                f"Unauthorized update attempt: user {current_user.id}, agent {agent_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own agents",
            )

        updated_agent = await agent_service.update_agent(
            agent_id, update_data, current_user.id
        )

        logger.info(
            f"Agent updated successfully: {agent_id} by user {current_user.id}"
        )
        return updated_agent

    except NotFoundError as e:
        logger.warning(f"Agent not found for update: {agent_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Not found", "message": str(e)},
        )
    except ValidationError as e:
        logger.warning(f"Agent update validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": "Validation failed", "message": str(e)},
        )
    except BusinessLogicError as e:
        logger.warning(f"Agent update business logic error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Business logic violation", "message": str(e)},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.delete("/{agent_id}", status_code=status.HTTP_200_OK)
async def delete_agent(
    agent_id: str,
    agent_service: AgentService = Depends(get_agent_service),
    current_user: User = Depends(get_current_user_dependency),
) -> JSONResponse:
    """
    Delete an agent with ownership verification and business rule checks.

    Args:
        agent_id: Agent identifier
        agent_service: Agent service dependency
        current_user: Authenticated user

    Returns:
        Success response with deletion confirmation

    Raises:
        HTTPException: If deletion fails or access denied
    """
    try:
        logger.info(
            f"User {current_user.id} attempting to delete agent {agent_id}"
        )

        # Verify ownership before attempting deletion
        if not verify_agent_ownership(agent_id, current_user):
            logger.warning(
                f"Unauthorized deletion attempt: user {current_user.id}, agent {agent_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own agents",
            )

        success = await agent_service.delete_agent(agent_id, current_user.id)

        if success:
            logger.info(
                f"Agent deleted successfully: {agent_id} by user {current_user.id}"
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Agent deleted successfully",
                    "agent_id": agent_id,
                    "deleted_by": current_user.id,
                },
            )
        else:
            logger.error(f"Agent deletion failed: {agent_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete agent",
            )

    except NotFoundError as e:
        logger.warning(f"Agent not found for deletion: {agent_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Not found", "message": str(e)},
        )
    except BusinessLogicError as e:
        logger.warning(f"Agent deletion business logic error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Business logic violation", "message": str(e)},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/{agent_id}/metrics", response_model=dict)
async def get_agent_metrics(
    agent_id: str,
    agent_service: AgentService = Depends(get_agent_service),
    current_user: User = Depends(get_current_user_dependency),
) -> dict:
    """
    Get comprehensive metrics for an agent.

    Args:
        agent_id: Agent identifier
        agent_service: Agent service dependency
        current_user: Authenticated user

    Returns:
        Agent metrics including reputation, negotiations, and influence scores
    """
    try:
        logger.info(
            f"User {current_user.id} requesting metrics for agent {agent_id}"
        )

        # Verify access to agent
        agent = await agent_service.get_agent_by_id(agent_id, current_user.id)

        if (
            not verify_agent_ownership(agent_id, current_user)
            and agent.status != "active"
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )

        # Get agent metrics (this would be implemented in the service)
        metrics = {
            "agent_id": agent_id,
            "reputation_score": agent.reputation_score,
            "total_negotiations": 0,  # Would be calculated from database
            "successful_negotiations": 0,  # Would be calculated from database
            "influence_score": 0.0,  # Would be calculated from influence service
            "last_activity": None,  # Would be fetched from database
        }

        return metrics

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting metrics for agent {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

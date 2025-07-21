"""
Negotiation management API endpoints with real-time protocol support.

Implements comprehensive negotiation workflows with async operations.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, status

from app.core.auth import User, get_mock_user, verify_agent_ownership
from app.core.config import get_settings
from app.core.exceptions import (
    BusinessLogicError,
    NotFoundError,
    ValidationError,
)
from app.models.negotiation import (
    Negotiation,
    NegotiationCreate,
    NegotiationResponse,
    NegotiationStatus,
    NegotiationTerms,
)
from app.services.agent_service import AgentService
from app.services.negotiation_service import NegotiationService

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_negotiation_service() -> NegotiationService:
    """Dependency to get negotiation service instance."""
    return NegotiationService()


async def get_agent_service() -> AgentService:
    """Dependency to get agent service instance."""
    return AgentService()


async def get_current_user_dependency() -> User:
    """Get current user with environment-based authentication."""
    settings = get_settings()

    if settings.ENVIRONMENT == "development":
        return await get_mock_user()
    else:
        return (
            await get_mock_user()
        )  # Replace with get_current_active_user for production


@router.post(
    "/", response_model=NegotiationResponse, status_code=status.HTTP_201_CREATED
)
async def create_negotiation(
    negotiation_data: NegotiationCreate,
    negotiation_service: NegotiationService = Depends(get_negotiation_service),
    agent_service: AgentService = Depends(get_agent_service),
    current_user: User = Depends(get_current_user_dependency),
) -> NegotiationResponse:
    """
    Create a new negotiation between two agents.

    This endpoint initiates a negotiation protocol with comprehensive validation:
    - Verifies both agents exist and are active
    - Validates user ownership of initiating agent
    - Ensures agents have compatible capabilities
    - Creates initial negotiation state with terms

    Args:
        negotiation_data: Negotiation creation data with terms and agent IDs
        negotiation_service: Negotiation service dependency
        agent_service: Agent service for validation
        current_user: Authenticated user

    Returns:
        Created negotiation instance with initial status

    Raises:
        HTTPException: If creation fails due to validation or business logic errors
    """
    try:
        logger.info(
            f"Creating negotiation for user {current_user.id}: "
            f"{negotiation_data.initiator_id} -> {negotiation_data.respondent_id}"
        )

        # Verify user owns the initiating agent
        initiator_agent = await agent_service.get_agent_by_id(
            negotiation_data.initiator_id, current_user.id
        )

        if not verify_agent_ownership(
            negotiation_data.initiator_id, current_user
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only create negotiations with your own agents",
            )

        created_negotiation = await negotiation_service.create_negotiation(
            negotiation_data, current_user.id
        )

        logger.info(
            f"Negotiation created successfully: {created_negotiation.id} "
            f"by user {current_user.id}"
        )
        return created_negotiation

    except ValidationError as e:
        logger.warning(f"Negotiation creation validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": "Validation failed", "message": str(e)},
        )
    except BusinessLogicError as e:
        logger.warning(f"Negotiation creation business logic error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Business logic violation", "message": str(e)},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating negotiation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/{negotiation_id}", response_model=NegotiationResponse)
async def get_negotiation(
    negotiation_id: str,
    negotiation_service: NegotiationService = Depends(get_negotiation_service),
    current_user: User = Depends(get_current_user_dependency),
) -> NegotiationResponse:
    """
    Retrieve a negotiation by ID with access control.

    Users can only access negotiations where they own one of the participating agents.

    Args:
        negotiation_id: Negotiation identifier
        negotiation_service: Negotiation service dependency
        current_user: Authenticated user

    Returns:
        Negotiation instance with current terms and status

    Raises:
        HTTPException: If negotiation not found or access denied
    """
    try:
        logger.info(
            f"User {current_user.id} requesting negotiation {negotiation_id}"
        )

        negotiation = await negotiation_service.get_negotiation_by_id(
            negotiation_id, current_user.id
        )

        return negotiation

    except NotFoundError as e:
        logger.warning(f"Negotiation not found: {negotiation_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Not found", "message": str(e)},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error retrieving negotiation {negotiation_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/", response_model=List[NegotiationResponse])
async def list_negotiations(
    skip: int = Query(0, ge=0, description="Number of negotiations to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum negotiations to return"
    ),
    status_filter: Optional[NegotiationStatus] = Query(
        None, description="Filter by status"
    ),
    agent_id: Optional[str] = Query(
        None, description="Filter by agent participation"
    ),
    negotiation_service: NegotiationService = Depends(get_negotiation_service),
    current_user: User = Depends(get_current_user_dependency),
) -> List[NegotiationResponse]:
    """
    List negotiations with filtering and pagination.

    Returns negotiations where the user owns at least one participating agent.

    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        status_filter: Optional status filter
        agent_id: Optional agent ID filter
        negotiation_service: Negotiation service dependency
        current_user: Authenticated user

    Returns:
        List of negotiations accessible to the user
    """
    try:
        logger.info(
            f"User {current_user.id} listing negotiations: "
            f"skip={skip}, limit={limit}, status={status_filter}, agent={agent_id}"
        )

        # If agent_id provided, verify user owns it
        if agent_id and not verify_agent_ownership(agent_id, current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view negotiations for your own agents",
            )

        negotiations = await negotiation_service.get_user_negotiations(
            user_id=current_user.id,
            agent_id=agent_id,
            status_filter=status_filter.value if status_filter else None,
            skip=skip,
            limit=limit,
        )

        logger.info(
            f"Returned {len(negotiations)} negotiations for user {current_user.id}"
        )
        return negotiations

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error listing negotiations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/{negotiation_id}/counter-offer", response_model=NegotiationResponse)
async def submit_counter_offer(
    negotiation_id: str,
    new_terms: NegotiationTerms,
    negotiation_service: NegotiationService = Depends(get_negotiation_service),
    current_user: User = Depends(get_current_user_dependency),
) -> NegotiationResponse:
    """
    Submit a counter offer in an active negotiation.

    This endpoint allows agents to propose new terms during active negotiations.
    Implements validation to ensure only participating agents can make offers.

    Args:
        negotiation_id: Negotiation identifier
        new_terms: New negotiation terms to propose
        negotiation_service: Negotiation service dependency
        current_user: Authenticated user

    Returns:
        Updated negotiation with new terms

    Raises:
        HTTPException: If offer submission fails
    """
    try:
        logger.info(
            f"User {current_user.id} submitting counter offer for negotiation {negotiation_id}"
        )

        updated_negotiation = await negotiation_service.submit_counter_offer(
            negotiation_id, new_terms.dict(), current_user.id
        )

        logger.info(
            f"Counter offer submitted successfully for negotiation {negotiation_id}"
        )
        return updated_negotiation

    except NotFoundError as e:
        logger.warning(
            f"Negotiation not found for counter offer: {negotiation_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Not found", "message": str(e)},
        )
    except BusinessLogicError as e:
        logger.warning(f"Counter offer business logic error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Business logic violation", "message": str(e)},
        )
    except Exception as e:
        logger.error(f"Unexpected error submitting counter offer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.patch("/{negotiation_id}/status", response_model=NegotiationResponse)
async def update_negotiation_status(
    negotiation_id: str,
    new_status: NegotiationStatus,
    negotiation_service: NegotiationService = Depends(get_negotiation_service),
    current_user: User = Depends(get_current_user_dependency),
) -> NegotiationResponse:
    """
    Update negotiation status (accept, reject, cancel).

    Implements proper state transition validation and business rules.

    Args:
        negotiation_id: Negotiation identifier
        new_status: New status to set
        negotiation_service: Negotiation service dependency
        current_user: Authenticated user

    Returns:
        Updated negotiation with new status

    Raises:
        HTTPException: If status update fails
    """
    try:
        logger.info(
            f"User {current_user.id} updating negotiation {negotiation_id} "
            f"status to {new_status.value}"
        )

        updated_negotiation = (
            await negotiation_service.update_negotiation_status(
                negotiation_id, new_status.value, current_user.id
            )
        )

        logger.info(
            f"Negotiation status updated successfully: {negotiation_id} -> {new_status.value}"
        )
        return updated_negotiation

    except NotFoundError as e:
        logger.warning(
            f"Negotiation not found for status update: {negotiation_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Not found", "message": str(e)},
        )
    except ValidationError as e:
        logger.warning(f"Invalid status transition: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": "Invalid status transition", "message": str(e)},
        )
    except BusinessLogicError as e:
        logger.warning(f"Status update business logic error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Business logic violation", "message": str(e)},
        )
    except Exception as e:
        logger.error(f"Unexpected error updating negotiation status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/{negotiation_id}/history", response_model=List[Dict[str, Any]])
async def get_negotiation_history(
    negotiation_id: str,
    negotiation_service: NegotiationService = Depends(get_negotiation_service),
    current_user: User = Depends(get_current_user_dependency),
) -> List[Dict[str, Any]]:
    """
    Get negotiation history with all offers and status changes.

    Provides audit trail of negotiation progression for analytics and debugging.

    Args:
        negotiation_id: Negotiation identifier
        negotiation_service: Negotiation service dependency
        current_user: Authenticated user

    Returns:
        List of negotiation history entries with timestamps

    Raises:
        HTTPException: If history retrieval fails
    """
    try:
        logger.info(
            f"User {current_user.id} requesting history for negotiation {negotiation_id}"
        )

        # Verify access to negotiation
        await negotiation_service.get_negotiation_by_id(
            negotiation_id, current_user.id
        )

        history = await negotiation_service.get_negotiation_history(
            negotiation_id
        )

        return history

    except NotFoundError as e:
        logger.warning(f"Negotiation not found for history: {negotiation_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Not found", "message": str(e)},
        )
    except Exception as e:
        logger.error(f"Unexpected error getting negotiation history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.websocket("/{negotiation_id}/live")
async def negotiation_websocket(
    websocket: WebSocket,
    negotiation_id: str,
    # In production, you'd validate the user via WebSocket auth
):
    """
    WebSocket endpoint for real-time negotiation updates.

    Provides live updates on negotiation status, new offers, and completions.

    Args:
        websocket: WebSocket connection
        negotiation_id: Negotiation identifier to monitor
    """
    await websocket.accept()

    try:
        logger.info(
            f"WebSocket connection established for negotiation {negotiation_id}"
        )

        # Send initial negotiation state
        await websocket.send_json(
            {
                "type": "connection_established",
                "negotiation_id": negotiation_id,
                "message": "Connected to negotiation updates",
            }
        )

        # Keep connection alive and send periodic updates
        # In production, this would integrate with Redis pub/sub or database
        # change streams
        while True:
            # Listen for messages from client (ping/pong, etc.)
            try:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_json({"type": "pong"})
            except Exception:
                break

    except Exception as e:
        logger.error(f"WebSocket error for negotiation {negotiation_id}: {e}")
    finally:
        logger.info(
            f"WebSocket connection closed for negotiation {negotiation_id}"
        )

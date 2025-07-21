"""
Agent Influence Broker - Negotiation API Routes

Comprehensive negotiation management endpoints implementing real-time
negotiation protocols, proposal handling, and state management following
FastAPI best practices with async/await patterns.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.logging import get_logger
from app.core.security import get_current_user_token
from app.schemas.negotiation import (
    NegotiationCreateRequest,
    NegotiationListResponse,
    NegotiationResponse,
    NegotiationSearchRequest,
    ProposalCreateRequest,
    ProposalResponse,
)
from app.services.negotiation_service import negotiation_engine

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/",
    response_model=NegotiationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create New Negotiation",
    description="Initiate a new negotiation between two agents",
)
async def create_negotiation(
    negotiation_data: NegotiationCreateRequest,
    current_user=Depends(get_current_user_token),
) -> NegotiationResponse:
    """Create new negotiation with comprehensive validation."""
    try:
        return await negotiation_engine.initiate_negotiation(
            negotiation_data, current_user.user_id
        )
    except Exception as e:
        logger.error(f"Negotiation creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create negotiation",
        )


@router.get(
    "/",
    response_model=NegotiationListResponse,
    summary="List Negotiations",
    description="Get paginated list of user's negotiations with filtering",
)
async def list_negotiations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
    current_user=Depends(get_current_user_token),
) -> NegotiationListResponse:
    """List user's negotiations with pagination and filtering."""
    try:
        search_params = NegotiationSearchRequest(
            page=page, page_size=page_size, status=status_filter
        )
        return await negotiation_engine.list_user_negotiations(
            current_user.user_id, search_params
        )
    except Exception as e:
        logger.error(f"Negotiation listing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list negotiations",
        )


@router.get(
    "/{negotiation_id}",
    response_model=NegotiationResponse,
    summary="Get Negotiation Details",
    description="Retrieve detailed negotiation information with proposal history",
)
async def get_negotiation(
    negotiation_id: str, current_user=Depends(get_current_user_token)
) -> NegotiationResponse:
    """Get detailed negotiation information."""
    try:
        return await negotiation_engine.get_negotiation(
            negotiation_id, current_user.user_id
        )
    except Exception as e:
        logger.error(f"Negotiation retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve negotiation",
        )


@router.post(
    "/{negotiation_id}/proposals",
    response_model=ProposalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit Proposal",
    description="Submit a new proposal in an active negotiation",
)
async def submit_proposal(
    negotiation_id: str,
    proposal_data: ProposalCreateRequest,
    current_user=Depends(get_current_user_token),
) -> ProposalResponse:
    """Submit proposal in negotiation."""
    try:
        return await negotiation_engine.submit_proposal(
            negotiation_id, proposal_data, current_user.user_id
        )
    except Exception as e:
        logger.error(f"Proposal submission failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit proposal",
        )

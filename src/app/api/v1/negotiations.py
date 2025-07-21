"""
Negotiation API routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid

from ..core.database import get_db_session
from ..core.security import require_user
from ..schemas.negotiations import (
    NegotiationCreate, NegotiationResponse, NegotiationUpdate,
    NegotiationMessageCreate, NegotiationMessageResponse
)

router = APIRouter()


@router.post("/", response_model=NegotiationResponse, status_code=status.HTTP_201_CREATED)
async def create_negotiation(
    negotiation_data: NegotiationCreate,
    current_user: dict = Depends(require_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new negotiation between agents"""
    # Implementation will be added with the service layer
    return {"message": "Negotiation creation endpoint"}


@router.get("/", response_model=List[NegotiationResponse])
async def list_negotiations(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    agent_id: Optional[uuid.UUID] = Query(None),
    current_user: dict = Depends(require_user),
    db: AsyncSession = Depends(get_db_session)
):
    """List negotiations with filtering"""
    # Implementation will be added with the service layer
    return []


@router.get("/{negotiation_id}", response_model=NegotiationResponse)
async def get_negotiation(
    negotiation_id: uuid.UUID,
    current_user: dict = Depends(require_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get negotiation by ID"""
    # Implementation will be added with the service layer
    return {"message": f"Get negotiation {negotiation_id}"}


@router.post("/{negotiation_id}/messages", response_model=NegotiationMessageResponse)
async def send_message(
    negotiation_id: uuid.UUID,
    message_data: NegotiationMessageCreate,
    current_user: dict = Depends(require_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Send a message in a negotiation"""
    # Implementation will be added with the service layer
    return {"message": "Message sent"}


@router.get("/{negotiation_id}/messages", response_model=List[NegotiationMessageResponse])
async def get_negotiation_messages(
    negotiation_id: uuid.UUID,
    current_user: dict = Depends(require_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get all messages in a negotiation"""
    # Implementation will be added with the service layer
    return []

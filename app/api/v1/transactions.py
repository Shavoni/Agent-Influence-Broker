"""
Agent Influence Broker - Transaction API Routes

Comprehensive transaction management endpoints implementing secure value exchange,
escrow management, and audit trails following FastAPI best practices.
"""

from typing import List

from fastapi import APIRouter, Depends, Query, status

from app.core.logging import get_logger
from app.core.security import get_current_user_token
from app.schemas.transaction import (
    TransactionCreateRequest,
    TransactionResponse,
)
from app.services.transaction_service import transaction_engine

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_transaction(
    transaction_data: TransactionCreateRequest,
    current_user=Depends(get_current_user_token),
):
    """Create new transaction with escrow."""
    return await transaction_engine.create_transaction(
        transaction_data, current_user.user_id
    )


@router.get("/", response_model=List[TransactionResponse])
async def list_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user=Depends(get_current_user_token),
):
    """List user's transactions."""
    return await transaction_engine.list_user_transactions(
        current_user.user_id, page, page_size
    )

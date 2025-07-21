"""
Transaction API routes
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid

from ..core.database import get_db_session
from ..core.security import require_user

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_transaction(
    current_user: dict = Depends(require_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new transaction"""
    return {"message": "Transaction creation endpoint"}


@router.get("/")
async def list_transactions(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(require_user),
    db: AsyncSession = Depends(get_db_session)
):
    """List transactions"""
    return {"message": "List transactions endpoint"}


@router.get("/{transaction_id}")
async def get_transaction(
    transaction_id: uuid.UUID,
    current_user: dict = Depends(require_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get transaction by ID"""
    return {"message": f"Get transaction {transaction_id}"}

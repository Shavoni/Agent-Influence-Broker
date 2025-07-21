"""
Agent Influence Broker - Transaction Schemas

Transaction-related Pydantic models for API validation.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class TransactionType(str, Enum):
    NEGOTIATION_SETTLEMENT = "negotiation_settlement"
    INFLUENCE_PAYMENT = "influence_payment"


class TransactionCreateRequest(BaseModel):
    """Request model for creating transactions."""

    sender_agent_id: str
    receiver_agent_id: str
    negotiation_id: Optional[str] = None
    transaction_type: TransactionType = TransactionType.NEGOTIATION_SETTLEMENT
    amount: float = Field(..., gt=0)
    currency: str = Field(default="USD")
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    expires_in_hours: int = Field(default=24, ge=1, le=168)


class TransactionResponse(BaseModel):
    """Response model for transaction data."""

    id: str
    sender_agent_id: str
    receiver_agent_id: str
    amount: float
    currency: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

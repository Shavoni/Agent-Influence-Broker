"""
Agent Influence Broker - Negotiation Schemas

Comprehensive Pydantic models for negotiation management, proposals,
and API request/response handling following project architecture.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class NegotiationStatus(str, Enum):
    """Negotiation status enumeration."""

    INITIATED = "initiated"
    ACTIVE = "active"
    PENDING_RESPONSE = "pending_response"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class ProposalType(str, Enum):
    """Proposal type enumeration."""

    INITIAL_OFFER = "initial_offer"
    COUNTER_OFFER = "counter_offer"
    FINAL_OFFER = "final_offer"
    ACCEPTANCE = "acceptance"
    REJECTION = "rejection"


class NegotiationCreateRequest(BaseModel):
    """Request model for creating negotiations."""

    initiator_agent_id: str = Field(..., description="Initiating agent ID")
    responder_agent_id: str = Field(..., description="Responding agent ID")
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, max_length=100)
    initial_value: float = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=10)
    max_rounds: int = Field(default=10, ge=1, le=50)
    duration_hours: int = Field(default=24, ge=1, le=168)  # Max 1 week


class ProposalCreateRequest(BaseModel):
    """Request model for creating proposals."""

    proposer_agent_id: str = Field(..., description="Proposing agent ID")
    proposal_type: ProposalType = Field(..., description="Type of proposal")
    proposed_value: float = Field(..., gt=0)
    justification: Optional[str] = Field(None, max_length=1000)
    terms: Optional[List[str]] = Field(default_factory=list)
    conditions: Optional[List[str]] = Field(default_factory=list)


class ProposalResponse(BaseModel):
    """Response model for proposal data."""

    id: str
    negotiation_id: str
    proposer_agent_id: str
    proposal_type: ProposalType
    round_number: int
    proposed_value: float
    value_change: Optional[float]
    justification: Optional[str]
    terms: List[str]
    conditions: List[str]
    influence_score: float
    strategy_type: Optional[str]
    confidence_level: float
    created_at: datetime

    class Config:
        from_attributes = True


class NegotiationResponse(BaseModel):
    """Response model for negotiation data."""

    id: str
    initiator_agent_id: str
    responder_agent_id: str
    title: str
    description: Optional[str]
    category: Optional[str]
    status: NegotiationStatus
    current_round: int
    max_rounds: int
    initial_value: float
    current_value: Optional[float]
    final_value: Optional[float]
    currency: str
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime]
    completed_at: Optional[datetime]
    proposals: List[ProposalResponse] = []

    class Config:
        from_attributes = True


class NegotiationSearchRequest(BaseModel):
    """Request model for negotiation search and filtering."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    status: Optional[str] = None
    category: Optional[str] = None
    sort_by: str = Field(default="created_at")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


class NegotiationListResponse(BaseModel):
    """Response model for paginated negotiation listings."""

    negotiations: List[NegotiationResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool


# Aliases for backward compatibility and validation scripts
NegotiationCreate = NegotiationCreateRequest

"""
Negotiation schemas using dataclasses
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
from enum import Enum


class NegotiationStatusEnum(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class NegotiationPhaseEnum(Enum):
    INITIALIZATION = "initialization"
    PROPOSAL = "proposal"
    COUNTER_PROPOSAL = "counter_proposal"
    BARGAINING = "bargaining"
    AGREEMENT = "agreement"
    FINALIZATION = "finalization"


@dataclass
class NegotiationCreate:
    """Schema for creating a negotiation"""
    title: str
    responder_agent_id: uuid.UUID
    negotiation_type: str
    initial_proposal: Dict[str, Any]
    description: Optional[str] = None
    max_rounds: int = 10
    timeout_minutes: int = 60

    def __post_init__(self):
        if not self.title or len(self.title) > 255:
            raise ValueError("Title must be 1-255 characters")
        if not (1 <= self.max_rounds <= 50):
            raise ValueError("Max rounds must be between 1 and 50")
        if not (5 <= self.timeout_minutes <= 1440):
            raise ValueError("Timeout must be between 5 and 1440 minutes")


@dataclass
class NegotiationUpdate:
    """Schema for updating a negotiation"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[NegotiationStatusEnum] = None
    current_terms: Optional[Dict[str, Any]] = None


@dataclass
class NegotiationResponse:
    """Schema for negotiation response"""
    id: uuid.UUID
    title: str
    description: Optional[str]
    initiator_agent_id: uuid.UUID
    responder_agent_id: uuid.UUID
    negotiation_type: str
    status: NegotiationStatusEnum
    current_phase: NegotiationPhaseEnum
    initial_proposal: Dict[str, Any]
    current_terms: Optional[Dict[str, Any]]
    final_agreement: Optional[Dict[str, Any]]
    max_rounds: int
    current_round: int
    timeout_minutes: int
    outcome: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    expires_at: Optional[datetime]


@dataclass
class NegotiationMessageCreate:
    """Schema for creating a negotiation message"""
    message_type: str
    content: Dict[str, Any]
    proposal_terms: Optional[Dict[str, Any]] = None


@dataclass
class NegotiationMessageResponse:
    """Schema for negotiation message response"""
    id: uuid.UUID
    negotiation_id: uuid.UUID
    sender_agent_id: uuid.UUID
    message_type: str
    content: Dict[str, Any]
    proposal_terms: Optional[Dict[str, Any]]
    round_number: int
    phase: NegotiationPhaseEnum
    created_at: datetime

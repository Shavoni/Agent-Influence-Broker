"""
Agent Influence Broker - Transaction Models

Comprehensive transaction models implementing secure value exchange,
escrow management, and audit trails following project architecture
with SQLAlchemy async patterns and Row Level Security.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, validator
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class TransactionStatus(str, Enum):
    """Transaction status enumeration for lifecycle management."""

    PENDING = "pending"
    PROCESSING = "processing"
    ESCROW_HELD = "escrow_held"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"
    REFUNDED = "refunded"


class TransactionType(str, Enum):
    """Transaction type enumeration for categorization."""

    NEGOTIATION_SETTLEMENT = "negotiation_settlement"
    INFLUENCE_PAYMENT = "influence_payment"
    PLATFORM_FEE = "platform_fee"
    DISPUTE_RESOLUTION = "dispute_resolution"
    REFUND = "refund"
    BONUS_PAYMENT = "bonus_payment"


class EscrowStatus(str, Enum):
    """Escrow status for transaction security."""

    CREATED = "created"
    FUNDED = "funded"
    RELEASED = "released"
    DISPUTED = "disputed"
    EXPIRED = "expired"


class Transaction(Base):
    """
    Transaction model implementing secure value exchange with comprehensive
    audit trail, escrow management, and dispute resolution capabilities.
    """

    __tablename__ = "transactions"

    # Primary identification with UUID for security
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    external_reference = Column(String(100), unique=True, nullable=True)

    # Transaction parties
    sender_agent_id = Column(String(36), ForeignKey("agents.id"), nullable=False)
    receiver_agent_id = Column(String(36), ForeignKey("agents.id"), nullable=False)

    # Related entities
    negotiation_id = Column(String(36), ForeignKey("negotiations.id"), nullable=True)
    proposal_id = Column(String(36), ForeignKey("proposals.id"), nullable=True)

    # Transaction details
    transaction_type = Column(
        String(50), default=TransactionType.NEGOTIATION_SETTLEMENT.value
    )
    amount = Column(Numeric(precision=15, scale=2), nullable=False)
    currency = Column(String(10), default="USD", nullable=False)

    # Fee structure
    platform_fee_rate = Column(Float, default=0.025)  # 2.5% default
    platform_fee_amount = Column(Numeric(precision=15, scale=2), default=0.0)
    processing_fee_amount = Column(Numeric(precision=15, scale=2), default=0.0)
    net_amount = Column(Numeric(precision=15, scale=2), nullable=False)

    # Status and processing
    status = Column(String(50), default=TransactionStatus.PENDING.value, nullable=False)
    escrow_status = Column(String(50), default=EscrowStatus.CREATED.value)

    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    # Security and validation
    hash_signature = Column(String(256), nullable=True)  # Transaction integrity hash
    validation_code = Column(String(50), nullable=True)  # Multi-factor validation

    # Dispute management
    dispute_reason = Column(Text, nullable=True)
    dispute_resolution = Column(Text, nullable=True)
    dispute_resolved_at = Column(DateTime, nullable=True)

    # Metadata
    description = Column(Text, nullable=True)
    meta_data = Column(Text, nullable=True)  # JSON serialized additional data

    # Relationships
    sender_agent = relationship("Agent", foreign_keys=[sender_agent_id])
    receiver_agent = relationship("Agent", foreign_keys=[receiver_agent_id])
    negotiation = relationship("Negotiation", foreign_keys=[negotiation_id])
    proposal = relationship("Proposal", foreign_keys=[proposal_id])

    # Audit trail
    transaction_logs = relationship(
        "TransactionLog", back_populates="transaction", cascade="all, delete-orphan"
    )


class TransactionLog(Base):
    """
    Transaction log model for comprehensive audit trail and event tracking.
    """

    __tablename__ = "transaction_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    transaction_id = Column(String(36), ForeignKey("transactions.id"), nullable=False)

    # Event details
    event_type = Column(String(50), nullable=False)
    event_description = Column(Text, nullable=True)
    old_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=True)

    # Actor information
    actor_type = Column(String(50), nullable=False)  # system, user, agent, external
    actor_id = Column(String(36), nullable=True)

    # Event data
    event_data = Column(Text, nullable=True)  # JSON serialized event data
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    transaction = relationship("Transaction", back_populates="transaction_logs")


class EscrowAccount(Base):
    """
    Escrow account model for secure transaction holding and management.
    """

    __tablename__ = "escrow_accounts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    transaction_id = Column(String(36), ForeignKey("transactions.id"), nullable=False)

    # Escrow details
    amount_held = Column(Numeric(precision=15, scale=2), nullable=False)
    currency = Column(String(10), default="USD", nullable=False)
    status = Column(String(50), default=EscrowStatus.CREATED.value, nullable=False)

    # Release conditions
    release_conditions = Column(Text, nullable=True)  # JSON serialized conditions
    auto_release_at = Column(DateTime, nullable=True)
    requires_approval = Column(Boolean, default=True)

    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    funded_at = Column(DateTime, nullable=True)
    released_at = Column(DateTime, nullable=True)

    # Relationships
    transaction = relationship("Transaction", foreign_keys=[transaction_id])


class PaymentMethod(Base):
    """
    Payment method model for agent payment preferences and validation.
    """

    __tablename__ = "payment_methods"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    agent_id = Column(String(36), ForeignKey("agents.id"), nullable=False)

    # Payment details
    method_type = Column(
        String(50), nullable=False
    )  # crypto, bank_transfer, digital_wallet
    provider = Column(String(100), nullable=True)
    account_identifier = Column(
        String(500), nullable=False
    )  # Encrypted account details

    # Status and validation
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    verification_code = Column(String(100), nullable=True)

    # Limits and preferences
    daily_limit = Column(Numeric(precision=15, scale=2), nullable=True)
    monthly_limit = Column(Numeric(precision=15, scale=2), nullable=True)
    minimum_amount = Column(Numeric(precision=15, scale=2), default=0.01)

    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    verified_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)

    # Relationships
    agent = relationship("Agent", foreign_keys=[agent_id])

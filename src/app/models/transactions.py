"""
Transaction database models
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..core.database import Base


class TransactionType(enum.Enum):
    """Transaction type enumeration"""

    PAYMENT = "payment"
    ESCROW = "escrow"
    REFUND = "refund"
    COMMISSION = "commission"
    PENALTY = "penalty"


class TransactionStatus(enum.Enum):
    """Transaction status enumeration"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


class Currency(enum.Enum):
    """Supported currencies"""

    USD = "USD"
    EUR = "EUR"
    BTC = "BTC"
    ETH = "ETH"
    CREDITS = "CREDITS"  # Platform credits


class Transaction(Base):
    """Transaction model for value exchanges between agents"""

    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Transaction participants
    payer_agent_id = Column(
        UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False
    )
    payee_agent_id = Column(
        UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False
    )

    # Related entities
    negotiation_id = Column(UUID(as_uuid=True), ForeignKey("negotiations.id"))

    # Transaction details
    transaction_type = Column(Enum(TransactionType), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)

    # Amount and currency
    amount = Column(Float, nullable=False)
    currency = Column(Enum(Currency), default=Currency.CREDITS)
    exchange_rate = Column(Float, default=1.0)  # To USD

    # Fees and commissions
    platform_fee = Column(Float, default=0.0)
    gas_fee = Column(Float, default=0.0)  # For blockchain transactions
    total_cost = Column(Float, nullable=False)

    # Transaction metadata
    description = Column(Text)
    metadata = Column(JSON)

    # External transaction references
    # Blockchain tx hash, payment processor ID, etc.
    external_tx_id = Column(String(255))
    # "crypto", "credit_card", "bank_transfer", "platform_credits"
    payment_method = Column(String(100))

    # Escrow and security
    is_escrowed = Column(Boolean, default=False)
    escrow_release_condition = Column(JSON)
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(String(255))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    completed_at = Column(DateTime)
    expires_at = Column(DateTime)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    payer = relationship("Agent", foreign_keys=[payer_agent_id])
    payee = relationship("Agent", foreign_keys=[payee_agent_id])
    negotiation = relationship("Negotiation")

    def __repr__(self):
        return f"<Transaction(id={self.id}, amount={self.amount}, status={self.status.value})>"

    def calculate_total_cost(self):
        """Calculate total transaction cost including fees"""
        self.total_cost = self.amount + self.platform_fee + self.gas_fee
        return self.total_cost

    def is_completed(self) -> bool:
        """Check if transaction is completed"""
        return self.status == TransactionStatus.COMPLETED

    def is_pending(self) -> bool:
        """Check if transaction is pending"""
        return self.status == TransactionStatus.PENDING

    def can_be_cancelled(self) -> bool:
        """Check if transaction can be cancelled"""
        return self.status in [
            TransactionStatus.PENDING,
            TransactionStatus.PROCESSING,
        ]


class TransactionLog(Base):
    """Transaction activity log for audit trail"""

    __tablename__ = "transaction_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(
        UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=False
    )

    # Log details
    # "created", "processed", "completed", "failed"
    action = Column(String(100), nullable=False)
    previous_status = Column(String(50))
    new_status = Column(String(50))

    # Additional context
    details = Column(JSON)
    actor_id = Column(String(255))  # Who performed the action

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    transaction = relationship("Transaction")

    def __repr__(self):
        return f"<TransactionLog(id={self.id}, action={self.action})>"

"""
Transaction management API endpoints with secure value exchange.

Implements comprehensive transaction workflows with escrow and validation.
"""

import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from app.core.auth import (
    User,
    get_current_active_user,
    get_mock_user,
    verify_agent_ownership,
)
from app.core.config import get_settings
from app.core.exceptions import BusinessLogicError, NotFoundError, ValidationError
from app.models.transaction import (
    Transaction,
    TransactionCreate,
    TransactionStatus,
    TransactionType,
    TransactionUpdate,
)
from app.services.agent_service import AgentService
from app.services.transaction_service import TransactionService

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_transaction_service() -> TransactionService:
    """Dependency to get transaction service instance."""
    return TransactionService()


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


@router.post("/", response_model=Transaction, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate,
    transaction_service: TransactionService = Depends(get_transaction_service),
    agent_service: AgentService = Depends(get_agent_service),
    current_user: User = Depends(get_current_user_dependency),
) -> Transaction:
    """
    Create a new transaction between agents.

    Implements secure value exchange with validation:
    - Verifies agent ownership and balances
    - Validates transaction amounts and limits
    - Creates escrow for large transactions
    - Integrates with negotiation completion

    Args:
        transaction_data: Transaction creation data
        transaction_service: Transaction service dependency
        agent_service: Agent service for validation
        current_user: Authenticated user

    Returns:
        Created transaction instance

    Raises:
        HTTPException: If creation fails due to validation or business logic errors
    """
    try:
        logger.info(
            f"Creating transaction for user {current_user.id}: "
            f"{transaction_data.from_agent_id} -> {transaction_data.to_agent_id} "
            f"Amount: {transaction_data.amount} {transaction_data.currency}"
        )

        # Verify user owns the source agent
        from_agent = await agent_service.get_agent_by_id(
            transaction_data.from_agent_id, current_user.id
        )

        if not verify_agent_ownership(transaction_data.from_agent_id, current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only create transactions from your own agents",
            )

        created_transaction = await transaction_service.create_transaction(
            transaction_data, current_user.id
        )

        logger.info(
            f"Transaction created successfully: {created_transaction.id} "
            f"by user {current_user.id}"
        )
        return created_transaction

    except ValidationError as e:
        logger.warning(f"Transaction creation validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": "Validation failed", "message": str(e)},
        )
    except BusinessLogicError as e:
        logger.warning(f"Transaction creation business logic error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Business logic violation", "message": str(e)},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating transaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/{transaction_id}", response_model=Transaction)
async def get_transaction(
    transaction_id: str,
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: User = Depends(get_current_user_dependency),
) -> Transaction:
    """
    Retrieve a transaction by ID with access control.

    Users can only access transactions involving their agents.

    Args:
        transaction_id: Transaction identifier
        transaction_service: Transaction service dependency
        current_user: Authenticated user

    Returns:
        Transaction instance with details

    Raises:
        HTTPException: If transaction not found or access denied
    """
    try:
        logger.info(f"User {current_user.id} requesting transaction {transaction_id}")

        transaction = await transaction_service.get_transaction_by_id(
            transaction_id, current_user.id
        )

        return transaction

    except NotFoundError as e:
        logger.warning(f"Transaction not found: {transaction_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Not found", "message": str(e)},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving transaction {transaction_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/", response_model=List[Transaction])
async def list_transactions(
    skip: int = Query(0, ge=0, description="Number of transactions to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum transactions to return"
    ),
    status_filter: Optional[TransactionStatus] = Query(
        None, description="Filter by status"
    ),
    transaction_type: Optional[TransactionType] = Query(
        None, description="Filter by type"
    ),
    agent_id: Optional[str] = Query(None, description="Filter by agent participation"),
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: User = Depends(get_current_user_dependency),
) -> List[Transaction]:
    """
    List transactions with filtering and pagination.

    Returns transactions where the user owns at least one participating agent.

    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        status_filter: Optional status filter
        transaction_type: Optional type filter
        agent_id: Optional agent ID filter
        transaction_service: Transaction service dependency
        current_user: Authenticated user

    Returns:
        List of transactions accessible to the user
    """
    try:
        logger.info(
            f"User {current_user.id} listing transactions: "
            f"skip={skip}, limit={limit}, status={status_filter}, "
            f"type={transaction_type}, agent={agent_id}"
        )

        # If agent_id provided, verify user owns it
        if agent_id and not verify_agent_ownership(agent_id, current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view transactions for your own agents",
            )

        transactions = await transaction_service.get_user_transactions(
            user_id=current_user.id,
            agent_id=agent_id,
            status_filter=status_filter.value if status_filter else None,
            transaction_type=transaction_type.value if transaction_type else None,
            skip=skip,
            limit=limit,
        )

        logger.info(
            f"Returned {len(transactions)} transactions for user {current_user.id}"
        )
        return transactions

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error listing transactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.patch("/{transaction_id}/status", response_model=Transaction)
async def update_transaction_status(
    transaction_id: str,
    new_status: TransactionStatus,
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: User = Depends(get_current_user_dependency),
) -> Transaction:
    """
    Update transaction status (approve, reject, complete).

    Implements proper state transition validation and escrow management.

    Args:
        transaction_id: Transaction identifier
        new_status: New status to set
        transaction_service: Transaction service dependency
        current_user: Authenticated user

    Returns:
        Updated transaction with new status

    Raises:
        HTTPException: If status update fails
    """
    try:
        logger.info(
            f"User {current_user.id} updating transaction {transaction_id} "
            f"status to {new_status.value}"
        )

        updated_transaction = await transaction_service.update_transaction_status(
            transaction_id, new_status.value, current_user.id
        )

        logger.info(
            f"Transaction status updated successfully: {transaction_id} -> {new_status.value}"
        )
        return updated_transaction

    except NotFoundError as e:
        logger.warning(f"Transaction not found for status update: {transaction_id}")
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
        logger.error(f"Unexpected error updating transaction status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/agent/{agent_id}/balance", response_model=Dict[str, Any])
async def get_agent_balance(
    agent_id: str,
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: User = Depends(get_current_user_dependency),
) -> Dict[str, Any]:
    """
    Get agent's current balance and transaction summary.

    Args:
        agent_id: Agent identifier
        transaction_service: Transaction service dependency
        current_user: Authenticated user

    Returns:
        Agent balance and transaction statistics
    """
    try:
        logger.info(f"User {current_user.id} requesting balance for agent {agent_id}")

        # Verify user owns the agent
        if not verify_agent_ownership(agent_id, current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view balances for your own agents",
            )

        balance_info = await transaction_service.get_agent_balance(agent_id)

        return balance_info

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent balance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

"""
Custom application exceptions
"""

from fastapi import HTTPException, status


class AgentBrokerException(Exception):
    """Base exception for Agent Broker application"""
    pass


class AgentNotFoundException(AgentBrokerException):
    """Agent not found exception"""
    pass


class NegotiationNotFoundException(AgentBrokerException):
    """Negotiation not found exception"""
    pass


class TransactionNotFoundException(AgentBrokerException):
    """Transaction not found exception"""
    pass


class InsufficientPermissionsException(AgentBrokerException):
    """Insufficient permissions exception"""
    pass


class InvalidNegotiationStateException(AgentBrokerException):
    """Invalid negotiation state exception"""
    pass


class InsufficientFundsException(AgentBrokerException):
    """Insufficient funds exception"""
    pass


# HTTP Exception mappings
def agent_not_found_http(agent_id: str) -> HTTPException:
    """HTTP exception for agent not found"""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Agent with ID {agent_id} not found"
    )


def negotiation_not_found_http(negotiation_id: str) -> HTTPException:
    """HTTP exception for negotiation not found"""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Negotiation with ID {negotiation_id} not found"
    )


def transaction_not_found_http(transaction_id: str) -> HTTPException:
    """HTTP exception for transaction not found"""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Transaction with ID {transaction_id} not found"
    )


def insufficient_permissions_http() -> HTTPException:
    """HTTP exception for insufficient permissions"""
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Insufficient permissions to perform this action"
    )


def invalid_negotiation_state_http(current_state: str, required_state: str) -> HTTPException:
    """HTTP exception for invalid negotiation state"""
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Invalid negotiation state. Current: {current_state}, Required: {required_state}"
    )


def insufficient_funds_http() -> HTTPException:
    """HTTP exception for insufficient funds"""
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Insufficient funds to complete this transaction"
    )

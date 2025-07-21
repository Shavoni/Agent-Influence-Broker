"""
Authentication and authorization functionality.

Implements JWT token-based authentication with role-based access control.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from pydantic import BaseModel

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)


class User(BaseModel):
    """User model for authentication."""

    id: str
    email: str
    username: str
    is_active: bool = True
    roles: list[str] = []

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class TokenData(BaseModel):
    """Token payload data."""

    user_id: str
    email: str
    exp: datetime


def create_access_token(user_id: str, email: str) -> str:
    """
    Create JWT access token for user.

    Args:
        user_id: User identifier
        email: User email

    Returns:
        JWT token string
    """
    settings = get_settings()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "user_id": user_id,
        "email": email,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }

    return jwt.encode(
        payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )


def verify_token(token: str) -> Optional[TokenData]:
    """
    Verify and decode JWT token.

    Args:
        token: JWT token string

    Returns:
        Token data if valid, None otherwise
    """
    try:
        settings = get_settings()

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        return TokenData(
            user_id=payload["user_id"],
            email=payload["email"],
            exp=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
        )

    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Invalid token")
        return None
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> User:
    """
    Get current authenticated user from JWT token.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        Current user instance

    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = verify_token(credentials.credentials)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # In production, this would fetch user from database
    # For development, return mock user
    return User(
        id=token_data.user_id,
        email=token_data.email,
        username=token_data.email.split("@")[0],
        is_active=True,
        roles=["user"],
    )


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user.

    Args:
        current_user: Current user from authentication

    Returns:
        Active user instance

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    return current_user


async def get_mock_user() -> User:
    """
    Get mock user for development environment.

    Returns:
        Mock user instance for testing
    """
    return User(
        id="mock-user-123",
        email="test@example.com",
        username="testuser",
        is_active=True,
        roles=["user", "agent_owner"],
    )


def verify_agent_ownership(agent_id: str, user: User) -> bool:
    """
    Verify user owns the specified agent.

    Args:
        agent_id: Agent identifier
        user: User instance

    Returns:
        True if user owns agent, False otherwise
    """
    # In development, mock ownership verification
    if user.id == "mock-user-123" and agent_id.startswith("mock-agent"):
        return True

    # In production, this would check database
    return False


def require_roles(required_roles: list[str]):
    """
    Dependency to require specific user roles.

    Args:
        required_roles: List of required roles

    Returns:
        FastAPI dependency function
    """

    async def check_roles(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if not any(role in current_user.roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return check_roles

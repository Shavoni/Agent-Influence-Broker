"""
Agent Influence Broker - Security & Authentication

Sophisticated JWT authentication with role-based access control,
comprehensive security measures, and proper error handling following
project architecture and security considerations.
"""

import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError

from app.core.config import get_settings
from app.core.logging import get_logger, log_security_event

logger = get_logger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token security
security = HTTPBearer()


class TokenData(BaseModel):
    """Token data validation model following Pydantic best practices."""

    username: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[str] = None
    scopes: list[str] = []


class Token(BaseModel):
    """JWT token response model with comprehensive metadata."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    role: str
    issued_at: datetime


class SecurityManager:
    """
    Comprehensive security manager implementing JWT authentication,
    password hashing, and role-based access control following
    project security considerations.
    """

    def __init__(self):
        """Initialize security manager with configuration."""
        self.settings = get_settings()
        self.secret_key = self.settings.SECRET_KEY
        self.algorithm = self.settings.ALGORITHM
        self.access_token_expire_minutes = (
            self.settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    def verify_password(
        self, plain_password: str, hashed_password: str
    ) -> bool:
        """
        Verify password against hash with comprehensive error handling.

        Args:
            plain_password: Plain text password to verify
            hashed_password: Stored password hash

        Returns:
            bool: True if password matches, False otherwise
        """
        try:
            result = pwd_context.verify(plain_password, hashed_password)
            if not result:
                log_security_event(
                    "password_verification_failed",
                    {"reason": "invalid_password"},
                    logger,
                )
            return result
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            log_security_event(
                "password_verification_error", {"error": str(e)}, logger
            )
            return False

    def get_password_hash(self, password: str) -> str:
        """
        Generate secure password hash with comprehensive validation.

        Args:
            password: Plain text password to hash

        Returns:
            str: Secure password hash

        Raises:
            ValueError: If password doesn't meet security requirements
        """
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        try:
            return pwd_context.hash(password)
        except Exception as e:
            logger.error(f"Password hashing error: {e}")
            raise ValueError("Failed to hash password")

    def create_access_token(
        self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token with comprehensive claims and validation.

        Args:
            data: Token payload data
            expires_delta: Optional custom expiration time

        Returns:
            str: Encoded JWT token

        Raises:
            ValueError: If token creation fails
        """
        try:
            to_encode = data.copy()

            # Set expiration time
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(
                    minutes=self.access_token_expire_minutes
                )

            # Add standard JWT claims
            to_encode.update(
                {
                    "exp": expire,
                    "iat": datetime.utcnow(),
                    "iss": "agent-influence-broker",
                    "aud": "agent-influence-broker-api",
                }
            )

            # Create token
            encoded_jwt = jwt.encode(
                to_encode, self.secret_key, algorithm=self.algorithm
            )

            log_security_event(
                "access_token_created",
                {
                    "user_id": data.get("sub"),
                    "role": data.get("role"),
                    "expires_at": expire.isoformat(),
                },
                logger,
            )

            return encoded_jwt

        except Exception as e:
            logger.error(f"Token creation error: {e}")
            log_security_event(
                "token_creation_failed",
                {"error": str(e), "user_id": data.get("sub")},
                logger,
            )
            raise ValueError("Failed to create access token")

    def verify_token(self, token: str) -> TokenData:
        """
        Verify and decode JWT token with comprehensive validation.

        Args:
            token: JWT token to verify

        Returns:
            TokenData: Decoded token data

        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            # Decode token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                audience="agent-influence-broker-api",
                issuer="agent-influence-broker",
            )

            # Extract token data
            username: str = payload.get("username")
            user_id: str = payload.get("sub")
            role: str = payload.get("role", "user")
            scopes: list = payload.get("scopes", [])

            if user_id is None:
                log_security_event(
                    "token_validation_failed",
                    {"reason": "missing_user_id"},
                    logger,
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing user identification",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            token_data = TokenData(
                username=username, user_id=user_id, role=role, scopes=scopes
            )

            return token_data

        except JWTError as e:
            log_security_event(
                "jwt_validation_failed",
                {"error": str(e), "error_type": type(e).__name__},
                logger,
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: JWT validation failed",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except ValidationError as e:
            log_security_event(
                "token_data_validation_failed", {"error": str(e)}, logger
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: malformed token data",
                headers={"WWW-Authenticate": "Bearer"},
            )


# Global security manager instance
security_manager = SecurityManager()


async def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenData:
    """
    Extract and validate current user from JWT token.

    FastAPI dependency for authentication middleware following
    dependency injection patterns and comprehensive error handling.

    Args:
        credentials: HTTP Bearer credentials from request

    Returns:
        TokenData: Validated token data for current user

    Raises:
        HTTPException: If authentication fails
    """
    try:
        token_data = security_manager.verify_token(credentials.credentials)
        return token_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        log_security_event("authentication_error", {"error": str(e)}, logger)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_role(required_role: str):
    """
    Role-based access control decorator for endpoints.

    Implements sophisticated RBAC following security considerations
    with comprehensive role validation and error handling.

    Args:
        required_role: Minimum required role for access

    Returns:
        Dependency function for FastAPI endpoint protection
    """

    # Role hierarchy for access control
    role_hierarchy = {"user": 1, "premium": 2, "moderator": 3, "admin": 4}

    async def check_role(
        current_user: TokenData = Depends(get_current_user_token),
    ) -> TokenData:
        """Check if current user has required role access."""

        user_role_level = role_hierarchy.get(current_user.role, 0)
        required_role_level = role_hierarchy.get(required_role, 999)

        if user_role_level < required_role_level:
            log_security_event(
                "access_denied_insufficient_role",
                {
                    "user_id": current_user.user_id,
                    "user_role": current_user.role,
                    "required_role": required_role,
                },
                logger,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient privileges. Required role: {required_role}",
            )

        return current_user

    return check_role


def require_scope(required_scope: str):
    """
    Scope-based access control for fine-grained permissions.

    Implements OAuth2-style scopes for granular access control
    following security best practices.

    Args:
        required_scope: Required scope for endpoint access

    Returns:
        Dependency function for scope validation
    """

    async def check_scope(
        current_user: TokenData = Depends(get_current_user_token),
    ) -> TokenData:
        """Check if current user has required scope."""

        if required_scope not in current_user.scopes:
            log_security_event(
                "access_denied_insufficient_scope",
                {
                    "user_id": current_user.user_id,
                    "required_scope": required_scope,
                    "user_scopes": current_user.scopes,
                },
                logger,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient scope. Required: {required_scope}",
            )

        return current_user

    return check_scope


# Utility functions for password security
def generate_secure_password(length: int = 16) -> str:
    """
    Generate cryptographically secure password.

    Args:
        length: Password length (minimum 12)

    Returns:
        str: Secure random password
    """
    if length < 12:
        length = 12

    return secrets.token_urlsafe(length)[:length]


def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Validate password strength against security requirements.

    Args:
        password: Password to validate

    Returns:
        Dict containing validation results and suggestions
    """
    validation = {
        "is_valid": True,
        "score": 0,
        "issues": [],
        "suggestions": [],
    }

    # Length check
    if len(password) < 8:
        validation["is_valid"] = False
        validation["issues"].append("Password too short")
        validation["suggestions"].append("Use at least 8 characters")
    else:
        validation["score"] += 20

    # Character variety checks
    if not any(c.isupper() for c in password):
        validation["issues"].append("No uppercase letters")
        validation["suggestions"].append("Add uppercase letters")
    else:
        validation["score"] += 20

    if not any(c.islower() for c in password):
        validation["issues"].append("No lowercase letters")
        validation["suggestions"].append("Add lowercase letters")
    else:
        validation["score"] += 20

    if not any(c.isdigit() for c in password):
        validation["issues"].append("No numbers")
        validation["suggestions"].append("Add numbers")
    else:
        validation["score"] += 20

    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        validation["issues"].append("No special characters")
        validation["suggestions"].append("Add special characters")
    else:
        validation["score"] += 20

    # Set validity based on score
    if validation["score"] < 60:
        validation["is_valid"] = False

    return validation

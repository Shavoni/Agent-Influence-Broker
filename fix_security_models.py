"""
Agent Influence Broker - Security and Models Setup

Implements security module and core database models following
project architecture and security considerations.
"""

import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def create_security_module() -> None:
    """Create security module with JWT and authentication."""

    security_content = '''"""
Agent Influence Broker - Security Module

Implements JWT authentication, password hashing, and security utilities
following FastAPI best practices and project security considerations.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()


class SecurityManager:
    """
    Comprehensive security management following project standards.
    
    Implements JWT token handling, password management, and
    authentication utilities with proper error handling.
    """
    
    def __init__(self):
        """Initialize security manager with settings."""
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token with expiration.
        
        Args:
            data: Token payload data
            expires_delta: Custom expiration time
            
        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            logger.info(f"Access token created for user: {data.get('sub')}")
            return encoded_jwt
        except Exception as e:
            logger.error(f"Token creation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create access token"
            )
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verify token hasn't expired
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return payload
            
        except JWTError as e:
            logger.warning(f"Token verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        try:
            return pwd_context.hash(password)
        except Exception as e:
            logger.error(f"Password hashing failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password processing failed"
            )
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False


# Global security manager instance
security_manager = SecurityManager()


async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract current user ID from JWT token."""
    try:
        payload = security_manager.verify_token(credentials.credentials)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user_id
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_user_token(user_id: str, email: str, role: str = "user") -> str:
    """Create user authentication token with role information."""
    token_data = {
        "sub": user_id,
        "email": email,
        "role": role,
        "type": "access_token"
    }
    
    return security_manager.create_access_token(token_data)


def require_role(required_role: str):
    """Decorator for role-based access control."""
    async def role_checker(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
        """Check if user has required role."""
        payload = security_manager.verify_token(credentials.credentials)
        user_role = payload.get("role", "user")
        
        if user_role != required_role and user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {required_role}"
            )
        
        return payload
    
    return role_checker
'''

    security_file = project_root / "app" / "core" / "security.py"
    security_file.write_text(security_content)
    print("✅ Created security module")


async def create_user_models() -> None:
    """Create user database models."""

    user_models_content = '''"""
Agent Influence Broker - User Models

Implements comprehensive user management with authentication,
profile management, and role-based access control.
"""

from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserRole(str, Enum):
    """User role enumeration for RBAC."""
    USER = "user"
    PREMIUM = "premium"
    ADMIN = "admin"
    MODERATOR = "moderator"


class UserStatus(str, Enum):
    """User status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class User(Base):
    """
    Comprehensive user model with authentication and profile management.
    
    Implements secure user management with JWT token support,
    role-based access control, and detailed profile tracking.
    """
    __tablename__ = "users"
    
    # Primary identification
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    
    # Authentication
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Role and permissions
    role = Column(String(20), default=UserRole.USER, index=True)
    subscription_tier = Column(String(20), default="free")
    
    # Profile information
    full_name = Column(String(100))
    avatar_url = Column(String(500))
    bio = Column(Text)
    
    # Usage and analytics
    last_login = Column(DateTime)
    total_negotiations = Column(Integer, default=0)
    reputation_score = Column(Float, default=0.0)
    
    # Account limits
    max_agents = Column(Integer, default=5)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    agents = relationship("Agent", back_populates="owner", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        """String representation of user."""
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    @property
    def is_premium(self) -> bool:
        """Check if user has premium subscription."""
        return self.subscription_tier in ["premium", "enterprise"]
    
    @property
    def can_create_agents(self) -> bool:
        """Check if user can create more agents."""
        agent_count = len(self.agents) if self.agents else 0
        return agent_count < self.max_agents
'''

    user_models_file = project_root / "app" / "models" / "user.py"
    user_models_file.write_text(user_models_content)
    print("✅ Created user models")


async def run_security_models_setup() -> None:
    """Execute security and models setup."""
    print("🔐 Setting up Security and Models")
    print("=" * 50)

    await create_security_module()
    await create_user_models()

    print("\n✅ Security and models setup completed!")
    print("🔧 Next step: Run python3 fix_agent_system.py")


if __name__ == "__main__":
    asyncio.run(run_security_models_setup())

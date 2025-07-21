"""
Immediate issue resolution script following project architecture.

Implements comprehensive fixes for current application import and
setup issues with detailed validation.
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Optional

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def fix_app_import_issues() -> bool:
    """
    Fix app import issues following project standards.

    Returns:
        True if fixes successful, False otherwise
    """
    print("🔧 Fixing Application Import Issues")
    print("=" * 50)

    # 1. Verify and fix file structure
    required_structure = {
        "app": ["__init__.py", "main.py"],
        "app/core": ["__init__.py", "config.py", "logging.py", "security.py", "database.py"],
        "app/api": ["__init__.py"],
        "app/api/v1": ["__init__.py", "api.py", "agents.py", "negotiations.py", "transactions.py"],
        "app/models": ["__init__.py", "user.py", "agent.py", "negotiation.py", "transaction.py"],
        "app/services": ["__init__.py", "agent_service.py", "negotiation_service.py", "transaction_service.py"],
        "app/schemas": ["__init__.py", "user.py", "agent.py", "negotiation.py", "transaction.py"],
        "app/utils": ["__init__.py", "auth.py", "validators.py"],
        "tests": ["__init__.py", "conftest.py"],
    }

    for directory, files in required_structure.items():
        dir_path = project_root / directory
        dir_path.mkdir(parents=True, exist_ok=True)

        for file in files:
            file_path = dir_path / file
            if not file_path.exists():
                if file == "__init__.py":
                    file_path.write_text(
                        f'"""Package initialization for {directory}."""\n'
                    )
                else:
                    file_path.touch()
                print(f"✅ Created {directory}/{file}")

    print("✅ File structure verification complete")
    return True


async def create_database_connection() -> None:
    """Create database connection module for Supabase integration."""
    
    database_content = '''"""
Agent Influence Broker - Database Connection

Implements async database operations with Supabase PostgreSQL
following project security considerations and RLS patterns.
"""

import asyncio
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Database base model
Base = declarative_base()

# Async engine for database connections
engine = None
async_session_maker = None


async def init_database() -> None:
    """
    Initialize database connection following async patterns.
    
    Implements connection pooling and error handling for Supabase.
    """
    global engine, async_session_maker
    
    try:
        # Create async engine for Supabase
        database_url = f"postgresql+asyncpg://{settings.SUPABASE_DB_USER}:{settings.SUPABASE_DB_PASSWORD}@{settings.SUPABASE_DB_HOST}:{settings.SUPABASE_DB_PORT}/{settings.SUPABASE_DB_NAME}"
        
        engine = create_async_engine(
            database_url,
            echo=settings.DEBUG,
            poolclass=NullPool,  # Supabase handles connection pooling
            pool_pre_ping=True,
            connect_args={
                "server_settings": {
                    "application_name": "agent-influence-broker",
                }
            }
        )
        
        # Create session maker
        async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        logger.info("✅ Database connection initialized")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get async database session following dependency injection patterns.
    
    Yields:
        AsyncSession for database operations
    """
    if async_session_maker is None:
        await init_database()
    
    async with async_session_maker() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_database() -> None:
    """Close database connections on shutdown."""
    global engine
    
    if engine:
        await engine.dispose()
        logger.info("✅ Database connections closed")
'''

    database_file = project_root / "app" / "core" / "database.py"
    database_file.write_text(database_content)
    print("✅ Created database connection module")


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
        """
        Hash password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        try:
            return pwd_context.hash(password)
        except Exception as e:
            logger.error(f"Password hashing failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password processing failed"
            )
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash.
        
        Args:
            plain_password: Plain text password
            hashed_password: Stored password hash
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False


# Global security manager instance
security_manager = SecurityManager()


async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Extract current user ID from JWT token.
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        User ID from token
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
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
    """
    Create user authentication token with role information.
    
    Args:
        user_id: User identifier
        email: User email address
        role: User role for RBAC
        
    Returns:
        JWT token string
    """
    token_data = {
        "sub": user_id,
        "email": email,
        "role": role,
        "type": "access_token"
    }
    
    return security_manager.create_access_token(token_data)


def require_role(required_role: str):
    """
    Decorator for role-based access control.
    
    Args:
        required_role: Required user role
        
    Returns:
        FastAPI dependency function
    """
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


async def create_agent_models() -> None:
    """Create agent-related database models."""
    
    agent_models_content = '''"""
Agent Influence Broker - Agent Models

Implements agent database models with capabilities, reputation,
and performance tracking following Supabase RLS patterns.
"""

from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AgentStatus(str, Enum):
    """Agent status enumeration for lifecycle management."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class ExperienceLevel(str, Enum):
    """Agent experience level enumeration."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class NegotiationStyle(str, Enum):
    """Negotiation style enumeration."""
    AGGRESSIVE = "aggressive"
    BALANCED = "balanced"
    CONSERVATIVE = "conservative"


class Agent(Base):
    """
    Agent model with comprehensive capability and reputation tracking.
    
    Implements sophisticated agent management following project
    architecture with performance analytics and security validations.
    """
    __tablename__ = "agents"
    
    # Primary identification
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    status = Column(String(20), default=AgentStatus.PENDING, index=True)
    
    # Owner relationship with foreign key
    owner_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    owner = relationship("User", back_populates="agents")
    
    # Agent capabilities and specializations
    capabilities = Column(ARRAY(String), default=list)
    specializations = Column(ARRAY(String), default=list)
    experience_level = Column(String(20), default=ExperienceLevel.BEGINNER)
    
    # Reputation and performance metrics
    reputation_score = Column(Float, default=0.0, index=True)
    influence_score = Column(Float, default=0.0, index=True)
    success_rate = Column(Float, default=0.0)
    total_negotiations = Column(Integer, default=0)
    completed_negotiations = Column(Integer, default=0)
    total_value_negotiated = Column(Float, default=0.0)
    
    # Agent configuration and preferences
    negotiation_style = Column(String(20), default=NegotiationStyle.BALANCED)
    max_concurrent_negotiations = Column(Integer, default=5)
    min_transaction_value = Column(Float, default=0.01)
    max_transaction_value = Column(Float, default=1000.0)
    
    # Availability and scheduling
    is_available = Column(Boolean, default=True)
    availability_schedule = Column(JSON, default=dict)  # Timezone and hours
    auto_accept_negotiations = Column(Boolean, default=False)
    
    # Agent AI configuration
    ai_model_preferences = Column(JSON, default=dict)
    learning_enabled = Column(Boolean, default=True)
    risk_tolerance = Column(Float, default=0.5)  # 0.0 = risk averse, 1.0 = risk seeking
    
    # Performance tracking
    average_negotiation_duration = Column(Float, default=0.0)  # Hours
    peer_ratings = Column(JSON, default=list)
    satisfaction_scores = Column(JSON, default=list)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    negotiations_initiated = relationship(
        "Negotiation", 
        foreign_keys="Negotiation.initiator_agent_id",
        back_populates="initiator_agent",
        cascade="all, delete-orphan"
    )
    negotiations_responded = relationship(
        "Negotiation", 
        foreign_keys="Negotiation.responder_agent_id",
        back_populates="responder_agent"
    )
    transactions_sent = relationship(
        "Transaction",
        foreign_keys="Transaction.from_agent_id",
        back_populates="from_agent"
    )
    transactions_received = relationship(
        "Transaction",
        foreign_keys="Transaction.to_agent_id", 
        back_populates="to_agent"
    )
    influence_metrics = relationship("InfluenceMetric", back_populates="agent", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        """String representation of agent."""
        return f"<Agent(id={self.id}, name='{self.name}', status='{self.status}')>"
    
    @property
    def is_active(self) -> bool:
        """Check if agent is active and available."""
        return self.status == AgentStatus.ACTIVE and self.is_available
    
    @property
    def reputation_tier(self) -> str:
        """Get reputation tier based on score."""
        if self.reputation_score >= 0.9:
            return "elite"
        elif self.reputation_score >= 0.7:
            return "expert"
        elif self.reputation_score >= 0.5:
            return "intermediate"
        elif self.reputation_score >= 0.3:
            return "novice"
        else:
            return "rookie"
    
    def can_negotiate_with(self, other_agent: "Agent") -> bool:
        """
        Check if this agent can negotiate with another agent.
        
        Args:
            other_agent: Target agent for negotiation
            
        Returns:
            True if negotiation is possible
        """
        # Basic validation checks
        if not self.is_active or not other_agent.is_active:
            return False
        
        if self.id == other_agent.id:
            return False
        
        # Check if agents have compatible experience levels
        experience_compatibility = {
            ExperienceLevel.BEGINNER: [ExperienceLevel.BEGINNER, ExperienceLevel.INTERMEDIATE],
            ExperienceLevel.INTERMEDIATE: [ExperienceLevel.BEGINNER, ExperienceLevel.INTERMEDIATE, ExperienceLevel.EXPERT],
            ExperienceLevel.EXPERT: [ExperienceLevel.INTERMEDIATE, ExperienceLevel.EXPERT]
        }
        
        return other_agent.experience_level in experience_compatibility.get(self.experience_level, [])
    
    def update_reputation(self, outcome_score: float, weight: float = 1.0) -> None:
        """
        Update agent reputation based on negotiation outcome.
        
        Args:
            outcome_score: Score from negotiation (0.0 - 1.0)
            weight: Weight factor for this update
        """
        # Weighted average update
        current_weight = self.total_negotiations
        total_weight = current_weight + weight
        
        if total_weight > 0:
            self.reputation_score = (
                (self.reputation_score * current_weight) + (outcome_score * weight)
            ) / total_weight
        else:
            self.reputation_score = outcome_score
        
        # Ensure score stays within bounds
        self.reputation_score = max(0.0, min(1.0, self.reputation_score))


class AgentCapability(Base):
    """
    Agent capability model for detailed skill tracking.
    
    Implements granular capability management with proficiency levels
    and certification tracking.
    """
    __tablename__ = "agent_capabilities"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    agent_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    
    # Capability details
    capability_name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # e.g., "technical", "business", "creative"
    proficiency_level = Column(Float, default=0.5)  # 0.0 - 1.0
    
    # Certification and validation
    is_certified = Column(Boolean, default=False)
    certification_date = Column(DateTime)
    certification_authority = Column(String(100))
    
    # Usage tracking
    times_used = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    last_used = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    agent = relationship("Agent", backref="detailed_capabilities")


class AgentRelationship(Base):
    """
    Agent relationship model for tracking interactions and trust.
    
    Implements relationship management between agents with trust scoring
    and interaction history.
    """
    __tablename__ = "agent_relationships"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Relationship participants
    agent_a_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    agent_b_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    
    # Relationship metrics
    trust_score = Column(Float, default=0.5)  # 0.0 - 1.0
    interaction_count = Column(Integer, default=0)
    successful_negotiations = Column(Integer, default=0)
    total_value_exchanged = Column(Float, default=0.0)
    
    # Relationship status
    relationship_type = Column(String(20), default="neutral")  # "ally", "rival", "neutral", "blocked"
    is_preferred_partner = Column(Boolean, default=False)
    
    # Timestamps
    first_interaction = Column(DateTime, default=datetime.utcnow)
    last_interaction = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    agent_a = relationship("Agent", foreign_keys=[agent_a_id])
    agent_b = relationship("Agent", foreign_keys=[agent_b_id])
    
    def update_trust(self, outcome_score: float) -> None:
        """
        Update trust score based on interaction outcome.
        
        Args:
            outcome_score: Outcome score (0.0 - 1.0)
        """
        # Exponential moving average for trust updates
        alpha = 0.2  # Learning rate
        self.trust_score = (1 - alpha) * self.trust_score + alpha * outcome_score
        self.trust_score = max(0.0, min(1.0, self.trust_score))
'''

    agent_models_file = project_root / "app" / "models" / "agent.py"
    agent_models_file.write_text(agent_models_content)
    print("✅ Created agent models")


async def create_agent_schemas() -> None:
    """Create agent Pydantic schemas."""
    
    agent_schemas_content = '''"""
Agent Influence Broker - Agent Schemas

Implements comprehensive Pydantic schemas for agent management
with validation, serialization, and API documentation.
"""

from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from uuid import UUID
from pydantic import BaseModel, Field, validator, root_validator


class AgentStatusEnum(str, Enum):
    """Agent status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class ExperienceLevelEnum(str, Enum):
    """Experience level enumeration."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class NegotiationStyleEnum(str, Enum):
    """Negotiation style enumeration."""
    AGGRESSIVE = "aggressive"
    BALANCED = "balanced"
    CONSERVATIVE = "conservative"


class AgentCapabilitySchema(BaseModel):
    """Schema for agent capability details."""
    name: str = Field(..., min_length=1, max_length=100, description="Capability name")
    category: str = Field(..., min_length=1, max_length=50, description="Capability category")
    proficiency_level: float = Field(default=0.5, ge=0.0, le=1.0, description="Proficiency level")
    is_certified: bool = Field(default=False, description="Certification status")


class AgentAvailabilitySchema(BaseModel):
    """Schema for agent availability configuration."""
    timezone: str = Field(default="UTC", description="Agent timezone")
    working_hours: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Working hours by day of week"
    )
    max_concurrent_negotiations: int = Field(
        default=5, ge=1, le=20, 
        description="Maximum concurrent negotiations"
    )


class AgentConfigurationSchema(BaseModel):
    """Schema for agent AI and behavior configuration."""
    risk_tolerance: float = Field(
        default=0.5, ge=0.0, le=1.0,
        description="Risk tolerance (0=conservative, 1=aggressive)"
    )
    learning_enabled: bool = Field(default=True, description="Enable learning from interactions")
    auto_accept_negotiations: bool = Field(default=False, description="Auto-accept compatible negotiations")
    min_transaction_value: float = Field(ge=0.01, description="Minimum transaction value")
    max_transaction_value: float = Field(ge=1.0, description="Maximum transaction value")
    
    @validator('max_transaction_value')
    def validate_transaction_range(cls, v, values):
        """Validate transaction value range."""
        min_value = values.get('min_transaction_value')
        if min_value and v <= min_value:
            raise ValueError('max_transaction_value must be greater than min_transaction_value')
        return v


class AgentBase(BaseModel):
    """Base agent schema with common fields."""
    name: str = Field(..., min_length=1, max_length=100, description="Agent name")
    description: Optional[str] = Field(None, max_length=2000, description="Agent description")
    capabilities: List[str] = Field(default_factory=list, description="Agent capabilities")
    specializations: List[str] = Field(default_factory=list, description="Agent specializations")
    experience_level: ExperienceLevelEnum = Field(default=ExperienceLevelEnum.BEGINNER)
    negotiation_style: NegotiationStyleEnum = Field(default=NegotiationStyleEnum.BALANCED)
    
    @validator('capabilities')
    def validate_capabilities(cls, v):
        """Validate capabilities list."""
        if len(v) > 20:
            raise ValueError('Maximum 20 capabilities allowed')
        return [cap.strip().lower() for cap in v if cap.strip()]
    
    @validator('specializations')
    def validate_specializations(cls, v):
        """Validate specializations list."""
        if len(v) > 10:
            raise ValueError('Maximum 10 specializations allowed')
        return [spec.strip().lower() for spec in v if spec.strip()]


class AgentCreate(AgentBase):
    """Schema for creating new agents."""
    configuration: AgentConfigurationSchema = Field(default_factory=AgentConfigurationSchema)
    availability: AgentAvailabilitySchema = Field(default_factory=AgentAvailabilitySchema)


class AgentUpdate(BaseModel):
    """Schema for updating existing agents."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    capabilities: Optional[List[str]] = None
    specializations: Optional[List[str]] = None
    negotiation_style: Optional[NegotiationStyleEnum] = None
    configuration: Optional[AgentConfigurationSchema] = None
    availability: Optional[AgentAvailabilitySchema] = None
    is_available: Optional[bool] = None


class AgentPerformanceMetrics(BaseModel):
    """Schema for agent performance metrics."""
    reputation_score: float = Field(..., ge=0.0, le=1.0, description="Agent reputation score")
    influence_score: float = Field(..., ge=0.0, description="Agent influence score")
    success_rate: float = Field(..., ge=0.0, le=1.0, description="Negotiation success rate")
    total_negotiations: int = Field(..., ge=0, description="Total negotiations count")
    completed_negotiations: int = Field(..., ge=0, description="Completed negotiations count")
    total_value_negotiated: float = Field(..., ge=0.0, description="Total value negotiated")
    average_negotiation_duration: float = Field(..., ge=0.0, description="Average duration in hours")
    reputation_tier: str = Field(..., description="Reputation tier classification")


class AgentResponse(AgentBase):
    """Schema for agent response data."""
    id: UUID
    owner_id: UUID
    status: AgentStatusEnum
    is_available: bool
    performance: AgentPerformanceMetrics
    created_at: datetime
    updated_at: datetime
    last_active: datetime
    
    class Config:
        from_attributes = True


class AgentSummary(BaseModel):
    """Schema for agent summary information."""
    id: UUID
    name: str
    status: AgentStatusEnum
    experience_level: ExperienceLevelEnum
    reputation_score: float
    capabilities: List[str]
    is_available: bool
    
    class Config:
        from_attributes = True


class AgentSearchFilters(BaseModel):
    """Schema for agent search and filtering."""
    status: Optional[AgentStatusEnum] = None
    experience_level: Optional[ExperienceLevelEnum] = None
    capabilities: Optional[List[str]] = None
    min_reputation: Optional[float] = Field(None, ge=0.0, le=1.0)
    max_reputation: Optional[float] = Field(None, ge=0.0, le=1.0)
    is_available: Optional[bool] = None
    owner_id: Optional[UUID] = None
    
    @validator('max_reputation')
    def validate_reputation_range(cls, v, values):
        """Validate reputation score range."""
        min_rep = values.get('min_reputation')
        if min_rep is not None and v is not None and v < min_rep:
            raise ValueError('max_reputation must be greater than min_reputation')
        return v


class AgentRegistrationRequest(BaseModel):
    """Schema for agent registration workflow."""
    agent_data: AgentCreate
    terms_accepted: bool = Field(..., description="Terms and conditions acceptance")
    privacy_consent: bool = Field(..., description="Privacy policy consent")
    
    @validator('terms_accepted')
    def validate_terms(cls, v):
        """Validate terms acceptance."""
        if not v:
            raise ValueError('Terms and conditions must be accepted')
        return v
    
    @validator('privacy_consent')
    def validate_privacy(cls, v):
        """Validate privacy consent."""
        if not v:
            raise ValueError('Privacy policy consent required')
        return v


class AgentAnalytics(BaseModel):
    """Schema for agent analytics and insights."""
    agent_id: UUID
    time_period: str = Field(..., description="Analytics time period")
    negotiation_metrics: Dict[str, Any] = Field(..., description="Negotiation performance")
    financial_metrics: Dict[str, Any] = Field(..., description="Financial performance")
    reputation_trends: List[Dict[str, Any]] = Field(..., description="Reputation trend data")
    peer_comparisons: Dict[str, Any] = Field(..., description="Peer comparison metrics")
    recommendations: List[str] = Field(..., description="Performance improvement recommendations")


class BulkAgentOperation(BaseModel):
    """Schema for bulk agent operations."""
    agent_ids: List[UUID] = Field(..., min_items=1, max_items=100, description="Agent IDs")
    operation: str = Field(..., description="Bulk operation type")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Operation parameters")
    
    @validator('operation')
    def validate_operation(cls, v):
        """Validate bulk operation type."""
        allowed_operations = ['activate', 'deactivate', 'suspend', 'update_config', 'delete']
        if v not in allowed_operations:
            raise ValueError(f'Operation must be one of: {allowed_operations}')
        return v
'''

    agent_schemas_file = project_root / "app" / "schemas" / "agent.py"
    agent_schemas_file.write_text(agent_schemas_content)
    print("✅ Created agent schemas")


async def create_agent_service() -> None:
    """Create agent service with business logic."""
    
    agent_service_content = '''"""
Agent Influence Broker - Agent Service

Implements comprehensive agent management with reputation tracking,
performance analytics, and business logic following project architecture.
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_, func, desc, asc
from fastapi import HTTPException, status

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.agent import Agent, AgentCapability, AgentRelationship
from app.schemas.agent import (
    AgentCreate, AgentUpdate, AgentResponse, AgentSummary,
    AgentSearchFilters, AgentAnalytics, AgentPerformanceMetrics
)

logger = get_logger(__name__)
settings = get_settings()


class AgentService:
    """
    Comprehensive agent management service following project architecture.
    
    Implements agent lifecycle management, reputation tracking,
    performance analytics, and relationship management.
    """
    
    def __init__(self, db: AsyncSession):
        """Initialize agent service with database session."""
        self.db = db
    
    async def create_agent(self, agent_data: AgentCreate, owner_id: UUID) -> AgentResponse:
        """
        Create new agent with comprehensive validation and initialization.
        
        Args:
            agent_data: Agent creation data
            owner_id: Owner user ID
            
        Returns:
            Created agent response
            
        Raises:
            HTTPException: If validation fails or creation error occurs
        """
        try:
            # Check agent limit per user
            user_agent_count = await self.db.execute(
                select(func.count(Agent.id)).where(Agent.owner_id == owner_id)
            )
            count = user_agent_count.scalar()
            
            if count >= settings.MAX_AGENTS_PER_USER:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Maximum {settings.MAX_AGENTS_PER_USER} agents allowed per user"
                )
            
            # Create agent with configuration
            agent = Agent(
                name=agent_data.name,
                description=agent_data.description,
                capabilities=agent_data.capabilities,
                specializations=agent_data.specializations,
                experience_level=agent_data.experience_level,
                negotiation_style=agent_data.negotiation_style,
                owner_id=owner_id,
                status="pending",
                # Configuration
                min_transaction_value=agent_data.configuration.min_transaction_value,
                max_transaction_value=agent_data.configuration.max_transaction_value,
                risk_tolerance=agent_data.configuration.risk_tolerance,
                learning_enabled=agent_data.configuration.learning_enabled,
                auto_accept_negotiations=agent_data.configuration.auto_accept_negotiations,
                # Availability
                max_concurrent_negotiations=agent_data.availability.max_concurrent_negotiations,
                availability_schedule=agent_data.availability.dict()
            )
            
            self.db.add(agent)
            await self.db.commit()
            await self.db.refresh(agent)
            
            # Create detailed capabilities
            for capability in agent_data.capabilities:
                capability_record = AgentCapability(
                    agent_id=agent.id,
                    capability_name=capability,
                    category="general",
                    proficiency_level=0.5
                )
                self.db.add(capability_record)
            
            await self.db.commit()
            
            logger.info(f"Created agent {agent.id} for user {owner_id}")
            return await self._build_agent_response(agent)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating agent: {e}")
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create agent"
            )
    
    async def get_agent(self, agent_id: UUID, owner_id: Optional[UUID] = None) -> Optional[AgentResponse]:
        """
        Get agent by ID with ownership validation.
        
        Args:
            agent_id: Agent identifier
            owner_id: Owner ID for authorization (optional)
            
        Returns:
            Agent response or None if not found
        """
        try:
            query = select(Agent).where(Agent.id == agent_id)
            
            if owner_id:
                query = query.where(Agent.owner_id == owner_id)
            
            result = await self.db.execute(query)
            agent = result.scalar_one_or_none()
            
            if agent:
                return await self._build_agent_response(agent)
            return None
            
        except Exception as e:
            logger.error(f"Error fetching agent {agent_id}: {e}")
            return None
    
    async def update_agent(
        self, 
        agent_id: UUID, 
        agent_data: AgentUpdate, 
        owner_id: UUID
    ) -> Optional[AgentResponse]:
        """
        Update agent with validation and ownership check.
        
        Args:
            agent_id: Agent identifier
            agent_data: Update data
            owner_id: Owner identifier for authorization
            
        Returns:
            Updated agent response or None if not found/unauthorized
        """
        try:
            result = await self.db.execute(
                select(Agent).where(
                    and_(Agent.id == agent_id, Agent.owner_id == owner_id)
                )
            )
            agent = result.scalar_one_or_none()
            
            if not agent:
                return None
            
            # Update fields
            update_data = agent_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if field in ['configuration', 'availability']:
                    # Handle nested configuration updates
                    if field == 'configuration' and value:
                        for config_field, config_value in value.items():
                            if hasattr(agent, config_field):
                                setattr(agent, config_field, config_value)
                    elif field == 'availability' and value:
                        agent.availability_schedule = value
                        if 'max_concurrent_negotiations' in value:
                            agent.max_concurrent_negotiations = value['max_concurrent_negotiations']
                else:
                    setattr(agent, field, value)
            
            agent.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(agent)
            
            logger.info(f"Updated agent {agent_id}")
            return await self._build_agent_response(agent)
            
        except Exception as e:
            logger.error(f"Error updating agent {agent_id}: {e}")
            await self.db.rollback()
            return None
    
    async def search_agents(
        self, 
        filters: AgentSearchFilters,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Search agents with filtering and pagination.
        
        Args:
            filters: Search filters
            page: Page number
            per_page: Items per page
            
        Returns:
            Search results with pagination
        """
        try:
            query = select(Agent)
            
            # Apply filters
            if filters.status:
                query = query.where(Agent.status == filters.status)
            
            if filters.experience_level:
                query = query.where(Agent.experience_level == filters.experience_level)
            
            if filters.capabilities:
                for capability in filters.capabilities:
                    query = query.where(Agent.capabilities.contains([capability]))
            
            if filters.min_reputation is not None:
                query = query.where(Agent.reputation_score >= filters.min_reputation)
            
            if filters.max_reputation is not None:
                query = query.where(Agent.reputation_score <= filters.max_reputation)
            
            if filters.is_available is not None:
                query = query.where(Agent.is_available == filters.is_available)
            
            if filters.owner_id:
                query = query.where(Agent.owner_id == filters.owner_id)
            
            # Count total results
            count_query = select(func.count(Agent.id))
            if query.whereclause is not None:
                count_query = count_query.where(query.whereclause)
            
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()
            
            # Apply pagination and ordering
            offset = (page - 1) * per_page
            query = query.order_by(desc(Agent.reputation_score), desc(Agent.last_active))
            query = query.limit(per_page).offset(offset)
            
            result = await self.db.execute(query)
            agents = result.scalars().all()
            
            # Build response
            agent_summaries = []
            for agent in agents:
                summary = AgentSummary(
                    id=agent.id,
                    name=agent.name,
                    status=agent.status,
                    experience_level=agent.experience_level,
                    reputation_score=agent.reputation_score,
                    capabilities=agent.capabilities or [],
                    is_available=agent.is_available
                )
                agent_summaries.append(summary)
            
            return {
                "agents": agent_summaries,
                "pagination": {
                    "total": total,
                    "page": page,
                    "per_page": per_page,
                    "pages": (total + per_page - 1) // per_page
                }
            }
            
        except Exception as e:
            logger.error(f"Error searching agents: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Search failed"
            )
    
    async def calculate_reputation(self, agent_id: UUID) -> float:
        """
        Calculate comprehensive agent reputation score.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Calculated reputation score (0.0 - 1.0)
        """
        try:
            # Get agent with performance data
            result = await self.db.execute(
                select(Agent).where(Agent.id == agent_id)
            )
            agent = result.scalar_one_or_none()
            
            if not agent:
                return 0.0
            
            # Reputation calculation components
            success_factor = agent.success_rate * 0.4  # 40% weight
            activity_factor = min(agent.total_negotiations / 50, 1.0) * 0.2  # 20% weight
            influence_factor = min(agent.influence_score / 100, 1.0) * 0.2  # 20% weight
            
            # Peer ratings factor
            peer_ratings = agent.peer_ratings or []
            if peer_ratings:
                avg_peer_rating = sum(peer_ratings) / len(peer_ratings)
                peer_factor = avg_peer_rating * 0.2  # 20% weight
            else:
                peer_factor = 0.0
            
            # Calculate final reputation
            reputation = success_factor + activity_factor + influence_factor + peer_factor
            reputation = max(0.0, min(1.0, reputation))
            
            # Update agent reputation
            agent.reputation_score = reputation
            await self.db.commit()
            
            logger.info(f"Updated reputation for agent {agent_id}: {reputation:.3f}")
            return reputation
            
        except Exception as e:
            logger.error(f"Error calculating reputation for agent {agent_id}: {e}")
            return 0.0
    
    async def get_agent_analytics(self, agent_id: UUID, time_period: str = "30d") -> AgentAnalytics:
        """
        Generate comprehensive analytics for agent performance.
        
        Args:
            agent_id: Agent identifier
            time_period: Analysis time period
            
        Returns:
            Agent analytics data
        """
        try:
            # Get agent data
            agent = await self.get_agent(agent_id)
            if not agent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Agent not found"
                )
            
            # Calculate time range
            days = int(time_period.rstrip('d'))
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Negotiation metrics (placeholder - would query negotiations table)
            negotiation_metrics = {
                "total_negotiations": agent.performance.total_negotiations,
                "success_rate": agent.performance.success_rate,
                "average_duration": agent.performance.average_negotiation_duration,
                "value_negotiated": agent.performance.total_value_negotiated
            }
            
            # Financial metrics
            financial_metrics = {
                "total_earnings": 0.0,  # Would calculate from transactions
                "average_transaction": 0.0,
                "commission_earned": 0.0
            }
            
            # Reputation trends (placeholder)
            reputation_trends = [
                {"date": datetime.utcnow().isoformat(), "score": agent.performance.reputation_score}
            ]
            
            # Peer comparisons
            peer_comparisons = {
                "reputation_percentile": 75.0,  # Would calculate against peers
                "activity_percentile": 80.0,
                "success_percentile": 70.0
            }
            
            # Recommendations
            recommendations = []
            if agent.performance.success_rate < 0.7:
                recommendations.append("Consider improving negotiation strategies")
            if agent.performance.reputation_score < 0.6:
                recommendations.append("Focus on building trust with peers")
            
            return AgentAnalytics(
                agent_id=agent_id,
                time_period=time_period,
                negotiation_metrics=negotiation_metrics,
                financial_metrics=financial_metrics,
                reputation_trends=reputation_trends,
                peer_comparisons=peer_comparisons,
                recommendations=recommendations
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating analytics for agent {agent_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Analytics generation failed"
            )
    
    async def _build_agent_response(self, agent: Agent) -> AgentResponse:
        """
        Build comprehensive agent response from model.
        
        Args:
            agent: Agent model instance
            
        Returns:
            Agent response schema
        """
        performance = AgentPerformanceMetrics(
            reputation_score=agent.reputation_score,
            influence_score=agent.influence_score,
            success_rate=agent.success_rate,
            total_negotiations=agent.total_negotiations,
            completed_negotiations=agent.completed_negotiations,
            total_value_negotiated=agent.total_value_negotiated,
            average_negotiation_duration=agent.average_negotiation_duration,
            reputation_tier=agent.reputation_tier
        )
        
        return AgentResponse(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            capabilities=agent.capabilities or [],
            specializations=agent.specializations or [],
            experience_level=agent.experience_level,
            negotiation_style=agent.negotiation_style,
            owner_id=agent.owner_id,
            status=agent.status,
            is_available=agent.is_available,
            performance=performance,
            created_at=agent.created_at,
            updated_at=agent.updated_at,
            last_active=agent.last_active
        )
'''

    agent_service_file = project_root / "app" / "services" / "agent_service.py"
    agent_service_file.write_text(agent_service_content)
    print("✅ Created agent service")


async def create_agent_api_endpoints() -> None:
    """Create agent API endpoints."""
    
    agent_api_content = '''"""
Agent Influence Broker - Agent API Endpoints

Implements comprehensive RESTful API for agent management
following FastAPI best practices and project architecture.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_database_session
from app.core.security import get_current_user_id, require_role
from app.core.logging import get_logger
from app.services.agent_service import AgentService
from app.schemas.agent import (
    AgentCreate, AgentUpdate, AgentResponse, AgentSummary,
    AgentSearchFilters, AgentAnalytics, AgentRegistrationRequest,
    BulkAgentOperation
)

logger = get_logger(__name__)

# Agent API router
router = APIRouter(prefix="/agents", tags=["Agents"])


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_request: AgentRegistrationRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_database_session)
) -> AgentResponse:
    """
    Create new agent with comprehensive validation.
    
    Args:
        agent_request: Agent registration request with terms acceptance
        current_user_id: Current authenticated user ID
        db: Database session
        
    Returns:
        Created agent response
        
    Raises:
        HTTPException: If creation fails or validation errors
    """
    try:
        agent_service = AgentService(db)
        user_uuid = UUID(current_user_id)
        
        agent = await agent_service.create_agent(
            agent_data=agent_request.agent_data,
            owner_id=user_uuid
        )
        
        logger.info(f"Agent created: {agent.id} by user {current_user_id}")
        return agent
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid UUID format: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agent creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Agent creation failed"
        )


@router.get("/", response_model=Dict[str, Any])
async def search_agents(
    status: Optional[str] = Query(None, description="Filter by agent status"),
    experience_level: Optional[str] = Query(None, description="Filter by experience level"),
    capabilities: Optional[List[str]] = Query(None, description="Filter by capabilities"),
    min_reputation: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum reputation score"),
    max_reputation: Optional[float] = Query(None, ge=0.0, le=1.0, description="Maximum reputation score"),
    is_available: Optional[bool] = Query(None, description="Filter by availability"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_database_session)
) -> Dict[str, Any]:
    """
    Search and filter agents with pagination.
    
    Args:
        status: Agent status filter
        experience_level: Experience level filter
        capabilities: Capabilities filter
        min_reputation: Minimum reputation score
        max_reputation: Maximum reputation score
        is_available: Availability filter
        page: Page number for pagination
        per_page: Items per page
        db: Database session
        
    Returns:
        Paginated search results
    """
    try:
        agent_service = AgentService(db)
        
        filters = AgentSearchFilters(
            status=status,
            experience_level=experience_level,
            capabilities=capabilities,
            min_reputation=min_reputation,
            max_reputation=max_reputation,
            is_available=is_available
        )
        
        results = await agent_service.search_agents(
            filters=filters,
            page=page,
            per_page=per_page
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Agent search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed"
        )


@router.get("/my", response_model=Dict[str, Any])
async def get_my_agents(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_database_session)
) -> Dict[str, Any]:
    """
    Get current user's agents with pagination.
    
    Args:
        page: Page number for pagination
        per_page: Items per page
        current_user_id: Current authenticated user ID
        db: Database session
        
    Returns:
        User's agents with pagination
    """
    try:
        agent_service = AgentService(db)
        user_uuid = UUID(current_user_id)
        
        filters = AgentSearchFilters(owner_id=user_uuid)
        results = await agent_service.search_agents(
            filters=filters,
            page=page,
            per_page=per_page
        )
        
        return results
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid UUID format: {str(e)}"
        )
    except Exception as e:
        logger.error(f"User agents fetch failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user agents"
        )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: UUID,
    db: AsyncSession = Depends(get_database_session)
) -> AgentResponse:
    """
    Get agent by ID with detailed information.
    
    Args:
        agent_id: Agent identifier
        db: Database session
        
    Returns:
        Agent detailed information
        
    Raises:
        HTTPException: If agent not found
    """
    try:
        agent_service = AgentService(db)
        agent = await agent_service.get_agent(agent_id)
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )
        
        return agent
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agent fetch failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch agent"
        )


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: UUID,
    agent_data: AgentUpdate,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_database_session)
) -> AgentResponse:
    """
    Update agent with ownership validation.
    
    Args:
        agent_id: Agent identifier
        agent_data: Update data
        current_user_id: Current authenticated user ID
        db: Database session
        
    Returns:
        Updated agent information
        
    Raises:
        HTTPException: If agent not found or unauthorized
    """
    try:
        agent_service = AgentService(db)
        user_uuid = UUID(current_user_id)
        
        agent = await agent_service.update_agent(
            agent_id=agent_id,
            agent_data=agent_data,
            owner_id=user_uuid
        )
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found or unauthorized"
            )
        
        logger.info(f"Agent updated: {agent_id} by user {current_user_id}")
        return agent
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid UUID format: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agent update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Agent update failed"
        )


@router.get("/{agent_id}/analytics", response_model=AgentAnalytics)
async def get_agent_analytics(
    agent_id: UUID,
    time_period: str = Query("30d", description="Analysis time period (e.g., 7d, 30d, 90d)"),
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_database_session)
) -> AgentAnalytics:
    """
    Get comprehensive agent analytics and performance metrics.
    
    Args:
        agent_id: Agent identifier
        time_period: Analysis time period
        current_user_id: Current authenticated user ID
        db: Database session
        
    Returns:
        Agent analytics data
        
    Raises:
        HTTPException: If agent not found or unauthorized
    """
    try:
        agent_service = AgentService(db)
        
        # Verify ownership
        user_uuid = UUID(current_user_id)
        agent = await agent_service.get_agent(agent_id, owner_id=user_uuid)
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found or unauthorized"
            )
        
        analytics = await agent_service.get_agent_analytics(
            agent_id=agent_id,
            time_period=time_period
        )
        
        return analytics
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid UUID format: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agent analytics failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analytics generation failed"
        )


@router.post("/{agent_id}/reputation/calculate")
async def calculate_agent_reputation(
    agent_id: UUID,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_database_session)
) -> Dict[str, float]:
    """
    Manually trigger reputation calculation for agent.
    
    Args:
        agent_id: Agent identifier
        current_user_id: Current authenticated user ID
        db: Database session
        
    Returns:
        Updated reputation score
        
    Raises:
        HTTPException: If agent not found or unauthorized
    """
    try:
        agent_service = AgentService(db)
        
        # Verify ownership
        user_uuid = UUID(current_user_id)
        agent = await agent_service.get_agent(agent_id, owner_id=user_uuid)
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found or unauthorized"
            )
        
        reputation_score = await agent_service.calculate_reputation(agent_id)
        
        logger.info(f"Reputation calculated for agent {agent_id}: {reputation_score}")
        return {"reputation_score": reputation_score}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid UUID format: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reputation calculation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Reputation calculation failed"
        )


async def run_initial_fixes() -> None:
    """Execute initial application fixes."""
    print("🔧 Running Initial Application Fixes")
    print("=" * 50)
    
    await fix_app_import_issues()
    await create_database_connection()
    
    print("\n✅ Initial fixes completed!")
    print("🔧 Next step: Run python3 fix_security_models.py")


if __name__ == "__main__":
    asyncio.run(run_initial_fixes())

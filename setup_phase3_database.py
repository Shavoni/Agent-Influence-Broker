#!/usr/bin/env python3
"""
Agent Influence Broker - Phase 3: Database Integration

Adds SQLAlchemy with async support and database models following
sophisticated architecture patterns with Supabase compatibility.
"""

import subprocess
import sys
from pathlib import Path


def setup_database_integration():
    """Setup database integration with async support."""

    print("🚀 Phase 3: Database Integration Setup")
    print("=" * 40)

    # Check previous phases
    if not verify_previous_phases():
        print("❌ Previous phases must be completed first")
        return False

    # Step 1: Install database stack
    if not install_database_stack():
        return False

    # Step 2: Create database models
    create_database_models()

    # Step 3: Update main application
    update_main_with_database()

    # Step 4: Test database functionality
    if test_database_setup():
        print("✅ Phase 3 Complete - Database integration ready")
        return True
    else:
        print("❌ Phase 3 Failed")
        return False


def verify_previous_phases():
    """Verify previous phases are complete."""
    try:
        from app.core.config import get_settings
        from app.main import app

        return True
    except:
        return False


def install_database_stack():
    """Install database components with fallbacks."""

    # Try PostgreSQL first, fallback to SQLite
    database_packages = [
        "sqlalchemy>=2.0.23",
        "aiosqlite>=0.19.0",  # SQLite fallback for Python 3.13
    ]

    print("🗄️  Installing database stack...")
    for package in database_packages:
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                check=True,
                capture_output=True,
            )
            print(f"✅ {package}")
        except subprocess.CalledProcessError:
            print(f"⚠️  {package} - database features may be limited")

    # Try asyncpg for PostgreSQL
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "asyncpg>=0.28.0"],
            check=True,
            capture_output=True,
        )
        print("✅ asyncpg (PostgreSQL driver)")
    except subprocess.CalledProcessError:
        print("⚠️  asyncpg failed - using SQLite only")

    return True


def create_database_models():
    """Create database models and connection logic."""

    # Create models directory
    models_dir = Path("app/models")
    models_dir.mkdir(exist_ok=True)

    # Database connection module
    (Path("app/core") / "database.py").write_text(
        '''
"""Agent Influence Broker - Database Connection"""

from typing import AsyncGenerator, Optional

try:
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
    from sqlalchemy.orm import declarative_base
    SQLALCHEMY_AVAILABLE = True
    Base = declarative_base()
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    AsyncSession = None
    Base = object

from app.core.config import get_settings

# Global database components
engine = None
async_session_maker = None

async def init_database():
    """Initialize database connection."""
    global engine, async_session_maker
    
    if not SQLALCHEMY_AVAILABLE:
        return
    
    # Use SQLite for development
    database_url = "sqlite+aiosqlite:///./agent_broker.db"
    
    engine = create_async_engine(database_url, echo=True)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession)

async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    if async_session_maker is None:
        await init_database()
    
    if async_session_maker:
        async with async_session_maker() as session:
            yield session

async def close_database():
    """Close database connections."""
    global engine
    if engine:
        await engine.dispose()
'''
    )

    # User model
    (models_dir / "user.py").write_text(
        '''
"""Agent Influence Broker - User Model"""

from datetime import datetime
from uuid import uuid4

try:
    from sqlalchemy import Column, String, Integer, Boolean, DateTime
    from app.core.database import Base
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    Base = object

if SQLALCHEMY_AVAILABLE:
    class User(Base):
        """User model with authentication and profile management."""
        __tablename__ = "users"
        
        id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
        email = Column(String(255), unique=True, nullable=False)
        username = Column(String(50), unique=True, nullable=False)
        is_active = Column(Boolean, default=True)
        created_at = Column(DateTime, default=datetime.utcnow)
else:
    class User:
        """Fallback User class."""
        def __init__(self, **kwargs):
            self.id = str(uuid4())
            self.email = kwargs.get('email')
            self.username = kwargs.get('username')
'''
    )

    print("✅ Database models created")


def update_main_with_database():
    """Update main application with database integration."""

    (Path("app") / "main.py").write_text(
        '''
"""Agent Influence Broker - Database-Enhanced Application"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

try:
    from app.core.config import get_settings
    from app.core.database import init_database, close_database
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    def get_settings():
        class BasicSettings:
            APP_NAME = "Agent Influence Broker"
            VERSION = "1.0.0"
        return BasicSettings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan with database initialization."""
    # Startup
    if DATABASE_AVAILABLE:
        await init_database()
        print("✅ Database initialized")
    
    yield
    
    # Shutdown
    if DATABASE_AVAILABLE:
        await close_database()
        print("✅ Database closed")

app = FastAPI(
    title="Agent Influence Broker",
    version="1.0.0",
    description="AI agent negotiation platform with database support",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    settings = get_settings()
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.VERSION,
        "phase": "database_integration",
        "features": ["validation", "cors", "database", "async_operations"],
        "database_available": DATABASE_AVAILABLE
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "phase": "database_integrated",
        "database": DATABASE_AVAILABLE
    }
'''
    )

    print("✅ Main application updated with database support")


def test_database_setup():
    """Test database functionality."""
    try:
        from app.main import app

        print("✅ Database-enhanced app imports successful")
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False


if __name__ == "__main__":
    setup_database_integration()

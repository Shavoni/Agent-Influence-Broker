"""
Database Configuration and Connection Management
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import structlog
from supabase import create_client, Client

from .config import settings

logger = structlog.get_logger(__name__)

# SQLAlchemy setup
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,
    future=True
)

async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()
metadata = MetaData()

# Supabase client
supabase: Client = None


async def get_db_session() -> AsyncSession:
    """Get database session dependency"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


def get_supabase_client() -> Client:
    """Get Supabase client"""
    global supabase
    if not supabase:
        supabase = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY
        )
    return supabase


async def init_db():
    """Initialize database"""
    try:
        async with engine.begin() as conn:
            # Create tables if they don't exist
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def close_db():
    """Close database connections"""
    await engine.dispose()
    logger.info("Database connections closed")

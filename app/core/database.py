"""Agent Influence Broker - Database Connection"""

from typing import AsyncGenerator

try:
    from sqlalchemy.ext.asyncio import (
        AsyncSession,
        async_sessionmaker,
        create_async_engine,
    )
    from sqlalchemy.orm import declarative_base

    SQLALCHEMY_AVAILABLE = True
    Base = declarative_base()
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    AsyncSession = None
    Base = object


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

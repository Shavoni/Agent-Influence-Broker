"""
Agent Influence Broker - API Integration Setup

Implements API endpoints and main application integration following
FastAPI best practices and project architecture.
"""

import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def create_main_api_router() -> None:
    """Create main API router."""

    api_content = '''"""
Agent Influence Broker - Main API Router

Integrates all API endpoints following FastAPI best practices
with comprehensive routing and documentation.
"""

from fastapi import APIRouter
from app.core.logging import get_logger

logger = get_logger(__name__)

# Main API router
router = APIRouter()

# Health check endpoints
@router.get("/health", tags=["System"])
async def system_health():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "service": "Agent Influence Broker API",
        "version": "1.0.0"
    }

@router.get("/version", tags=["System"])
async def api_version():
    """API version information."""
    return {
        "version": "1.0.0",
        "api_version": "v1",
        "features": ["agent_management", "negotiations", "transactions"]
    }
'''

    api_file = project_root / "app" / "api" / "v1" / "api.py"
    api_file.write_text(api_content)
    print("✅ Created main API router")


async def update_main_application() -> None:
    """Update main FastAPI application."""

    main_content = '''"""
Agent Influence Broker - Main FastAPI Application

Sophisticated FastAPI application implementing AI agent negotiation,
influence tracking, and transaction management.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings, get_cors_origins
from app.core.logging import setup_logging, get_logger
from app.api.v1.api import router as api_v1_router

# Initialize logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan management."""
    # Startup
    logger.info("🚀 Starting Agent Influence Broker")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Agent Influence Broker")


def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    
    # Create FastAPI application
    application = FastAPI(
        title="Agent Influence Broker",
        description="AI agent negotiation and influence platform",
        version="1.0.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )
    
    # Configure CORS
    cors_origins = get_cors_origins()
    application.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    # Global exception handler
    @application.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Global exception handler."""
        logger.error(f"Global exception in {request.url}: {exc}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )
    
    # Include API routes
    application.include_router(
        api_v1_router,
        prefix="/api/v1",
        tags=["API v1"]
    )
    
    # Root endpoint
    @application.get("/", tags=["Root"])
    async def root():
        """Root endpoint."""
        return {
            "message": "Welcome to Agent Influence Broker",
            "version": "1.0.0",
            "docs": "/docs" if settings.DEBUG else "Documentation disabled",
            "api": "/api/v1"
        }
    
    logger.info("🏗️ FastAPI application configured")
    return application


# Create application instance
app = create_application()
'''

    main_file = project_root / "app" / "main.py"
    main_file.write_text(main_content)
    print("✅ Updated main application")


async def run_api_integration() -> None:
    """Execute API integration setup."""
    print("🔗 Setting up API Integration")
    print("=" * 50)

    await create_main_api_router()
    await update_main_application()

    print("\n✅ API integration completed!")
    print("🔧 Next step: Run python3 test_complete_setup.py")


if __name__ == "__main__":
    asyncio.run(run_api_integration())

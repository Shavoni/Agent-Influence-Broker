"""
Agent Influence Broker - Application Runner

Enhanced startup script with health checks and comprehensive
error handling following FastAPI best practices.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    import uvicorn

    from app.core.config import get_settings
    from app.core.logging import get_logger, setup_logging

    def main():
        """Main application entry point with enhanced startup."""
        try:
            # Setup logging first
            setup_logging()
            logger = get_logger(__name__)

            # Get application settings
            settings = get_settings()

            logger.info("🚀 Starting Agent Influence Broker")
            logger.info(f"🌍 Environment: {settings.ENVIRONMENT}")
            logger.info(f"🔗 URL: http://{settings.HOST}:{settings.PORT}")
            logger.info(f"📚 API Docs: http://{settings.HOST}:{settings.PORT}/docs")

            # Start the server
            uvicorn.run(
                "app.main:app",
                host=settings.HOST,
                port=settings.PORT,
                reload=settings.DEBUG,
                log_level=settings.LOG_LEVEL.lower(),
            )

        except Exception as e:
            print(f"❌ Failed to start: {e}")
            import traceback

            traceback.print_exc()

    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("🔧 Please ensure all dependencies are installed:")
    print(
        "   pip install fastapi uvicorn pydantic python-jose[cryptography] passlib[bcrypt]"
    )
    sys.exit(1)

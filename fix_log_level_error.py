#!/usr/bin/env python3
"""
Quick fix for the LOG_LEVEL attribute error in Agent Influence Broker setup
"""

from pathlib import Path


def fix_logging_configuration():
    """Fix the logging configuration to use correct attribute names."""

    print("🔧 Fixing LOG_LEVEL attribute error...")

    # Fixed logging configuration
    logging_content = '''"""
Agent Influence Broker - Fixed Logging Configuration

Corrected logging setup that properly accesses settings attributes
following project architecture standards.
"""

import logging
import sys
from pathlib import Path

def setup_logging(log_level: str = "INFO"):
    """
    Setup logging with proper error handling and attribute access.
    
    Args:
        log_level: Logging level string (INFO, DEBUG, WARNING, ERROR)
    """
    try:
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Configure logging with proper handlers
        logging.basicConfig(
            level=getattr(logging, log_level.upper(), logging.INFO),
            format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(logs_dir / "agent_broker.log", encoding='utf-8')
            ],
            force=True  # Override any existing configuration
        )
        
        # Set external library log levels
        logging.getLogger("uvicorn").setLevel(logging.INFO)
        logging.getLogger("uvicorn.access").setLevel(logging.INFO)
        
    except Exception as e:
        # Fallback to basic stdout logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)]
        )
        print(f"⚠️  Logging setup warning: {e}")

def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance with consistent configuration.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)

# Initialize logging on module import
try:
    from app.core.config import get_settings
    settings = get_settings()
    # Access LOG_LEVEL correctly (it exists in your Settings class)
    setup_logging(settings.LOG_LEVEL)
except (ImportError, AttributeError):
    # Fallback if settings not available or attribute missing
    setup_logging("INFO")
'''

    # Write fixed logging module
    config_dir = Path("app") / "core"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "logging.py").write_text(logging_content)

    print("✅ Fixed logging configuration")
    return True


def fix_settings_configuration():
    """Ensure Settings class has all required attributes."""

    # Enhanced settings with all required attributes
    config_content = '''"""
Agent Influence Broker - Enhanced Settings Configuration

Complete settings class with all required attributes for logging
and application configuration following project standards.
"""

import os
from typing import List, Optional

class Settings:
    """
    Enhanced settings class with complete attribute coverage.
    
    Includes all attributes referenced throughout the application
    to prevent AttributeError exceptions.
    """
    
    # Application metadata
    APP_NAME: str = "Agent Influence Broker"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Sophisticated AI agent negotiation and influence platform"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Server configuration
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # Security settings
    SECRET_KEY: str = "dev-secret-key-change-in-production-32-chars-minimum"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS and host settings
    ALLOWED_HOSTS: List[str] = ["*"]
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Logging configuration - THIS WAS MISSING
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    
    # Application limits
    MAX_AGENTS_PER_USER: int = 10
    MAX_CONCURRENT_NEGOTIATIONS: int = 50
    
    # Database configuration (SQLite for development)
    DATABASE_URL: str = "sqlite+aiosqlite:///./agent_broker.db"
    
    # Webhook settings
    WEBHOOK_TIMEOUT: int = 30
    WEBHOOK_RETRY_ATTEMPTS: int = 3
    
    def __init__(self):
        """Initialize settings with environment variable overrides."""
        # Override with environment variables if available
        self.APP_NAME = os.getenv("APP_NAME", self.APP_NAME)
        self.DEBUG = os.getenv("DEBUG", "true").lower() == "true"
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", self.ENVIRONMENT)
        self.HOST = os.getenv("HOST", self.HOST)
        self.PORT = int(os.getenv("PORT", str(self.PORT)))
        self.SECRET_KEY = os.getenv("SECRET_KEY", self.SECRET_KEY)
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", self.LOG_LEVEL)
        self.DATABASE_URL = os.getenv("DATABASE_URL", self.DATABASE_URL)

# Global settings instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """
    Get settings instance following singleton pattern.
    
    Returns:
        Settings instance with all required attributes
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

def get_cors_origins() -> List[str]:
    """Get CORS origins based on environment."""
    settings = get_settings()
    return ["*"] if settings.DEBUG else settings.CORS_ORIGINS

def get_database_url() -> str:
    """Get database URL with environment configuration."""
    settings = get_settings()
    return settings.DATABASE_URL
'''

    # Write enhanced settings
    config_dir = Path("app") / "core"
    (config_dir / "config.py").write_text(config_content)

    print("✅ Enhanced settings configuration with LOG_LEVEL attribute")
    return True


def test_fixed_configuration():
    """Test that the fixed configuration works."""

    try:
        # Test settings import and attribute access
        from app.core.config import get_settings

        settings = get_settings()

        # Test that LOG_LEVEL attribute exists
        log_level = settings.LOG_LEVEL
        print(f"✅ LOG_LEVEL attribute accessible: {log_level}")

        # Test logging import
        from app.core.logging import get_logger

        logger = get_logger(__name__)

        print(f"✅ Logger created successfully: {logger.name}")

        # Test a log message
        logger.info("Configuration test successful")
        print("✅ Logging system working")

        return True

    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main execution to fix the LOG_LEVEL error."""

    print("🔧 Fixing Agent Influence Broker LOG_LEVEL Error")
    print("=" * 50)

    # Step 1: Fix settings configuration
    if not fix_settings_configuration():
        print("❌ Failed to fix settings")
        return False

    # Step 2: Fix logging configuration
    if not fix_logging_configuration():
        print("❌ Failed to fix logging")
        return False

    # Step 3: Test the fixes
    if test_fixed_configuration():
        print("\n✅ LOG_LEVEL error fixed successfully!")
        print("🚀 You can now proceed with your application")
        return True
    else:
        print("\n❌ Fix verification failed")
        return False


if __name__ == "__main__":
    main()

# Quick test script
python3 -c "
from app.core.config import get_settings
from app.core.logging import get_logger
settings = get_settings()
print(f'✅ LOG_LEVEL: {settings.LOG_LEVEL}')
logger = get_logger('test')
logger.info('Test successful')
"

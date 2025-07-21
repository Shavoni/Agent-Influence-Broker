"""
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
    DESCRIPTION: str = (
        "Sophisticated AI agent negotiation and influence platform"
    )
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
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

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


# Global settings instance for easy access
settings = get_settings()

"""
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

def log_security_event(event_type: str, details: dict, logger: logging.Logger) -> None:
    """
    Log security-related events with structured data.
    
    Args:
        event_type: Type of security event
        details: Additional event details
        logger: Logger instance to use
    """
    try:
        event_data = {
            "event_type": event_type,
            "details": details,
            "timestamp": logging.Formatter().formatTime(logging.LogRecord(
                name="security", level=logging.INFO, pathname="", lineno=0,
                msg="", args=(), exc_info=None
            ))
        }
        logger.warning(f"Security Event: {event_type} | Details: {details}")
    except Exception as e:
        logger.error(f"Failed to log security event: {e}")

# Initialize logging on module import
try:
    from app.core.config import get_settings
    settings = get_settings()
    # Access LOG_LEVEL correctly (it exists in your Settings class)
    setup_logging(settings.LOG_LEVEL)
except (ImportError, AttributeError):
    # Fallback if settings not available or attribute missing
    setup_logging("INFO")

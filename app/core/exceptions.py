"""
Custom exception handling for Agent Influence Broker.

Implements comprehensive error handling following FastAPI best practices
and the project's security considerations.
"""

import logging
import traceback
from typing import Any, Dict, Optional

logger = logging.getLogger("app.exceptions")


class ApplicationError(Exception):
    """
    Base application exception following project error handling standards.

    Implements structured error information with proper logging integration.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize application error with comprehensive context.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional error context
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "APPLICATION_ERROR"
        self.details = details or {}

        # Log error following comprehensive logging strategy
        logger.error(
            f"Application error: {self.error_code} - {message}",
            extra={"error_code": self.error_code, "details": self.details},
        )


class AppImportError(ApplicationError):
    """
    Specific exception for application import failures.

    Follows project exception handling with detailed diagnostic information.
    """

    def __init__(self, original_error: Exception, component: str):
        """
        Initialize app import error with diagnostic context.

        Args:
            original_error: The original exception that caused the import failure
            component: Name of the component that failed to import
        """
        message = f"Failed to import {component}: {str(original_error)}"
        details = {
            "component": component,
            "original_error_type": type(original_error).__name__,
            "original_error": str(original_error),
            "traceback": traceback.format_exc(),
        }

        super().__init__(
            message=message, error_code="APP_IMPORT_ERROR", details=details
        )


class BusinessLogicError(ApplicationError):
    """Exception for business logic violations."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "BUSINESS_LOGIC_ERROR", details)


class NotFoundError(ApplicationError):
    """Exception for resource not found errors."""
    
    def __init__(self, resource: str, identifier: str, details: Optional[Dict[str, Any]] = None):
        message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(message, "NOT_FOUND_ERROR", details)


class ValidationError(ApplicationError):
    """Exception for data validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        error_details = details or {}
        if field:
            error_details["field"] = field
        super().__init__(message, "VALIDATION_ERROR", error_details)


def safe_app_import() -> Optional[Any]:
    """
    Safely import FastAPI app with comprehensive error handling.

    Implements project error handling standards with detailed diagnostics
    and recovery suggestions.

    Returns:
        FastAPI app instance if successful, None if failed
    """
    try:
        from app.main import app

        logger.info("✅ FastAPI application imported successfully")
        return app

    except ImportError as e:
        error = AppImportError(e, "app.main")
        print(f"❌ App import failed: {error.message}")

        # Provide specific guidance based on import error
        if "app.core" in str(e):
            print("🔧 Fix: Ensure app/core/__init__.py exists")
            print("🔧 Fix: Check app/core/config.py and app/core/logging.py")
        elif "fastapi" in str(e):
            print("🔧 Fix: Install FastAPI: pip install fastapi")
        elif "pydantic" in str(e):
            print("🔧 Fix: Install Pydantic: pip install pydantic")
        else:
            print(f"🔧 Fix: Check import path and dependencies")

        return None

    except Exception as e:
        error = AppImportError(e, "app.main")
        print(f"❌ Unexpected error during app import: {error.message}")
        print(f"📋 Error type: {type(e).__name__}")

        if logger.isEnabledFor(logging.DEBUG):
            print("🔍 Full traceback:")
            traceback.print_exc()

        return None


def format_error_message(error: Exception, context: str = "") -> str:
    """
    Format error messages following project logging standards.

    Args:
        error: The exception to format
        context: Additional context about where the error occurred

    Returns:
        Formatted error message string
    """
    base_message = f"❌ {context} failed" if context else "❌ Error occurred"
    error_details = f": {str(error)}"

    # Use string concatenation to avoid f-string quote issues
    return base_message + error_details


def print_diagnostic_info(error: Exception, component: str) -> None:
    """
    Print diagnostic information following project error handling.

    Args:
        error: The exception that occurred
        component: Name of the component that failed
    """
    print("=" * 60)
    print(f"🚨 DIAGNOSTIC INFO: {component}")
    print("=" * 60)
    print(f"Error Type: {type(error).__name__}")
    print(f"Error Message: {str(error)}")

    # Get error details without f-string issues
    if hasattr(error, "__cause__") and error.__cause__:
        print(f"Caused by: {type(error.__cause__).__name__}: {str(error.__cause__)}")

    print("=" * 60)

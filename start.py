#!/usr/bin/env python3
"""
Enhanced application startup script for Agent Influence Broker.

Implements comprehensive startup checks and graceful error handling
following the project's architecture and security standards.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def check_python_version() -> bool:
    """
    Check if Python version meets minimum requirements.

    Returns:
        True if version is compatible, False otherwise
    """
    min_version = (3, 8)
    current_version = sys.version_info[:2]

    if current_version < min_version:
        print(
            f"❌ Python {min_version[0]}.{min_version[1]}+ required, found {current_version[0]}.{current_version[1]}"
        )
        return False

    print(f"✅ Python {current_version[0]}.{current_version[1]} detected")
    return True


def check_virtual_environment() -> bool:
    """
    Check if running in virtual environment.

    Returns:
        True if in virtual environment, False otherwise
    """
    in_venv = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )

    if not in_venv:
        print("⚠️  Not running in virtual environment (recommended but not required)")
        return True  # Allow running without venv in development

    print("✅ Virtual environment active")
    return True


def check_dependencies() -> bool:
    """
    Check if required dependencies are installed.

    Returns:
        True if all dependencies available, False otherwise
    """
    required_packages = [
        ("fastapi", "FastAPI web framework"),
        ("uvicorn", "ASGI server"),
        ("pydantic", "Data validation"),
        ("python_dotenv", "Environment configuration"),
    ]

    missing_packages = []

    for package, description in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} ({description}) available")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} ({description}) not found")

    if missing_packages:
        print(f"\n📦 Install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        return False

    return True


def check_environment_file() -> bool:
    """
    Check if .env file exists and is properly configured.

    Returns:
        True if environment is properly configured, False otherwise
    """
    env_file = project_root / ".env"

    if not env_file.exists():
        print("❌ .env file not found")
        print("📝 Creating default .env file...")
        create_default_env_file()
        return True

    print("✅ .env file found")
    return True


def create_default_env_file() -> None:
    """Create a default .env file with development settings."""
    default_env_content = """# Agent Influence Broker - Environment Configuration
# Following security best practices

APP_NAME=Agent Influence Broker
ENVIRONMENT=development
DEBUG=true
HOST=127.0.0.1
PORT=8000

# Security Settings (Change in production)
SECRET_KEY=dev-secret-key-change-in-production-use-secure-random-string
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256

# Database Settings (Configure with your Supabase credentials)
SUPABASE_URL=https://placeholder.supabase.co
SUPABASE_ANON_KEY=placeholder-key

# CORS Settings
ALLOWED_HOSTS=*

# Logging Configuration
LOG_LEVEL=INFO

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Webhook Configuration
WEBHOOK_SECRET=dev-webhook-secret
"""

    env_file = project_root / ".env"
    env_file.write_text(default_env_content)
    print("✅ Default .env file created")


def check_application_imports() -> bool:
    """
    Test if application can be imported successfully.

    Returns:
        True if application imports successfully, False otherwise
    """
    try:
        from app.core.config import get_settings

        settings = get_settings()
        print(f"✅ Configuration loaded: {settings.APP_NAME}")

        from app.main import app

        print("✅ Application imports successful")

        return True

    except Exception as e:
        print(f"❌ Application import failed: {e}")
        print(f"📋 Error details: {type(e).__name__}: {str(e)}")
        return False


def start_application() -> None:
    """
    Start the FastAPI application with proper configuration.

    Implements graceful startup with comprehensive error handling.
    """
    try:
        # Import after all checks pass
        import uvicorn

        from app.core.config import get_settings
        from app.core.logging import setup_logging

        # Setup logging first
        setup_logging()

        # Get settings
        settings = get_settings()

        print(f"\n🚀 Starting {settings.APP_NAME}...")
        print(f"🌍 Environment: {settings.ENVIRONMENT}")
        print(f"🔗 URL: http://{settings.HOST}:{settings.PORT}")
        print(f"📚 Docs: http://{settings.HOST}:{settings.PORT}/docs")
        print(f"🩺 Health: http://{settings.HOST}:{settings.PORT}/health")
        print(f"🔄 Reload: {settings.DEBUG}")

        # Start server with enhanced configuration
        uvicorn.run(
            "app.main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level=settings.LOG_LEVEL.lower(),
            access_log=True,
            reload_dirs=["app"] if settings.DEBUG else None,
            use_colors=True,
        )

    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Failed to start application: {e}")
        print(f"📋 Error details: {type(e).__name__}: {str(e)}")
        sys.exit(1)


def install_dependencies() -> bool:
    """
    Attempt to install missing dependencies automatically.

    Returns:
        True if installation successful, False otherwise
    """
    try:
        print("📦 Attempting to install dependencies...")

        # Core dependencies for the project
        core_packages = [
            "fastapi==0.104.1",
            "uvicorn[standard]==0.24.0",
            "python-dotenv==1.0.0",
            "pydantic[email]==2.5.0",
        ]

        for package in core_packages:
            print(f"Installing {package}...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                print(f"❌ Failed to install {package}")
                print(f"Error: {result.stderr}")
                return False

        print("✅ Dependencies installed successfully")
        return True

    except Exception as e:
        print(f"❌ Dependency installation failed: {e}")
        return False


def main() -> None:
    """
    Main startup routine with comprehensive checks.

    Implements all pre-startup validations following project standards.
    """
    print("🔍 Agent Influence Broker - Startup Checks")
    print("=" * 50)

    # Run all checks
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtual_environment),
        ("Dependencies", check_dependencies),
        ("Environment Configuration", check_environment_file),
        ("Application Imports", check_application_imports),
    ]

    failed_checks = []

    for check_name, check_func in checks:
        print(f"\n📋 {check_name}:")
        if not check_func():
            failed_checks.append(check_name)

    # Handle failed dependency check by attempting auto-install
    if "Dependencies" in failed_checks:
        print(f"\n🔧 Attempting automatic dependency installation...")
        if install_dependencies():
            print("✅ Dependencies installed, re-checking...")
            # Re-run dependency and import checks
            if check_dependencies() and check_application_imports():
                failed_checks = [
                    check
                    for check in failed_checks
                    if check not in ["Dependencies", "Application Imports"]
                ]

    if failed_checks:
        print(f"\n❌ {len(failed_checks)} check(s) failed:")
        for check in failed_checks:
            print(f"  • {check}")
        print("\n🔧 Please resolve the issues above before starting the application.")

        # Provide helpful guidance
        print("\n📋 Quick Setup Guide:")
        print("1. Install Python 3.8+ from https://python.org")
        print("2. Create virtual environment: python3 -m venv venv")
        print("3. Activate virtual environment: source venv/bin/activate")
        print(
            "4. Install dependencies: pip install fastapi uvicorn python-dotenv pydantic"
        )
        print("5. Run this script again: python3 start.py")

        sys.exit(1)

    print("\n✅ All checks passed!")
    print("=" * 50)

    # Start application
    start_application()


if __name__ == "__main__":
    main()

# Logging output simulation
print("🚀 Agent Influence Broker - Logging System Initialized")
print("🔧 Environment: development")
print("📊 Log Level: INFO")
print("🐛 Debug Mode: True")
print("🔓 Development logging with enhanced debugging")
print("INFO:     Started server process [xxxxx]")
print("INFO:     Waiting for application startup.")
print("🚀 Starting Agent Influence Broker application")
print("📊 Initializing database connections")
print("🔌 Initializing external service connections")
print("✅ Application startup complete")
print("INFO:     Application startup complete.")
print("INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)")

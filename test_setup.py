#!/usr/bin/env python3
"""
Test script to verify Agent Influence Broker setup.

Quick verification of project dependencies and configuration.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_imports():
    """Test all critical imports."""
    print("🧪 Testing imports...")

    try:
        import fastapi

        print(f"✅ FastAPI {fastapi.__version__}")
    except ImportError as e:
        print(f"❌ FastAPI: {e}")
        return False

    try:
        import uvicorn

        print(f"✅ Uvicorn available")
    except ImportError as e:
        print(f"❌ Uvicorn: {e}")
        return False

    try:
        import pydantic

        print(f"✅ Pydantic {pydantic.__version__}")
    except ImportError as e:
        print(f"❌ Pydantic: {e}")
        return False

    try:
        from dotenv import load_dotenv

        print(f"✅ Python-dotenv available")
    except ImportError as e:
        print(f"❌ Python-dotenv: {e}")
        return False

    return True


def test_app_imports():
    """Test application-specific imports."""
    print("\n🧪 Testing application imports...")

    try:
        from app.core.config import get_settings

        settings = get_settings()
        print(f"✅ Settings: {settings.APP_NAME}")
    except Exception as e:
        print(f"❌ Settings: {e}")
        return False

    try:
        from app.main import app

        print(f"✅ FastAPI app created")
    except Exception as e:
        print(f"❌ App creation: {e}")
        return False

    return True


def main():
    """Run all tests."""
    print("🔍 Agent Influence Broker - Setup Test")
    print("=" * 40)

    if not test_imports():
        print("\n❌ Core imports failed - install dependencies first")
        print("Run: pip install fastapi uvicorn python-dotenv pydantic")
        return False

    if not test_app_imports():
        print("\n❌ Application imports failed - check app structure")
        return False

    print("\n✅ All tests passed! Ready to start the application.")
    print("Run: python3 start.py")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

"""
Enhanced app import testing following project testing strategy.

Implements comprehensive error handling and diagnostics with proper
string formatting and FastAPI best practices.
"""

import sys
import traceback
from pathlib import Path
from typing import Any, Optional

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_app_import_with_diagnostics() -> bool:
    """
    Test app import with comprehensive diagnostics.

    Following project testing strategy and error handling standards.

    Returns:
        True if import successful, False otherwise
    """
    print("🔍 Testing FastAPI Application Import")
    print("=" * 50)

    try:
        # Test step by step following project architecture
        print("📋 Step 1: Testing configuration import...")
        from app.core.config import get_settings

        settings = get_settings()
        print("✅ Configuration import successful")
        print("App Name: {}".format(settings.APP_NAME))
        print("Environment: {}".format(settings.ENVIRONMENT))

        print("\n📋 Step 2: Testing logging import...")
        from app.core.logging import setup_logging

        print("✅ Logging import successful")

        print("\n📋 Step 3: Testing FastAPI app import...")
        from app.main import app

        print("✅ FastAPI app import successful")
        print("App Title: {}".format(app.title))
        print("App Version: {}".format(app.version))

        # Test app functionality
        print("\n📋 Step 4: Testing app functionality...")
        middleware_count = len(app.user_middleware)
        print("Middleware Count: {}".format(middleware_count))

        print("\n✅ All import tests passed!")
        return True

    except ImportError as e:
        print("❌ Import Error: {}".format(str(e)))

        # Specific guidance based on error
        error_str = str(e)
        if "app.core" in error_str:
            print("🔧 Issue: Missing core module")
            print("🔧 Fix: Check app/core/__init__.py exists")
        elif "fastapi" in error_str:
            print("🔧 Issue: FastAPI not installed")
            print("🔧 Fix: pip install fastapi")
        elif "pydantic" in error_str:
            print("🔧 Issue: Pydantic not installed")
            print("🔧 Fix: pip install pydantic")

        return False

    except Exception as e:
        print("❌ Unexpected Error: {}".format(str(e)))
        print("Error Type: {}".format(type(e).__name__))

        print("\n🔍 Full traceback:")
        traceback.print_exc()

        return False


def main() -> None:
    """
    Main test routine following project standards.
    """
    print("🚀 Agent Influence Broker - App Import Test")
    print("Following FastAPI best practices and project architecture")
    print("=" * 70)

    success = test_app_import_with_diagnostics()

    if success:
        print("\n🎉 Success! FastAPI application is ready.")
        print("🚀 Next: python3 run.py")
    else:
        print("\n❌ Import test failed. Review errors above.")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

{
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "editor.formatOnSave": true,
    "python.analysis.typeCheckingMode": "basic",
}

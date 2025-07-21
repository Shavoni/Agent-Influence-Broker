"""
Quick installation test for Agent Influence Broker.

Verifies that all critical components are working following
the project's architecture and testing standards.
"""

import sys


def test_critical_imports():
    """Test all critical imports with detailed error reporting."""
    print("🧪 Testing critical imports...")

    imports_to_test = [
        ("fastapi", "FastAPI web framework"),
        ("uvicorn", "ASGI server"),
        ("pydantic", "Data validation"),
        ("dotenv", "Environment configuration"),
    ]

    all_passed = True

    for module, description in imports_to_test:
        try:
            imported = __import__(module)
            version = getattr(imported, "__version__", "unknown")
            print(f"✅ {module} v{version} - {description}")
        except ImportError as e:
            print(f"❌ {module} - {description}: {e}")
            all_passed = False

    return all_passed


def test_app_creation():
    """Test application creation following project structure."""
    print("\n🧪 Testing application creation...")

    try:
        from app.core.config import get_settings

        settings = get_settings()
        print(f"✅ Configuration loaded: {settings.APP_NAME}")

        from app.main import app

        print("✅ FastAPI application created successfully")

        return True

    except Exception as e:
        print(f"❌ Application creation failed: {e}")
        return False


def main():
    """Run installation tests."""
    print("🔍 Agent Influence Broker - Installation Test")
    print("=" * 50)

    if not test_critical_imports():
        print("\n❌ Critical imports failed")
        return False

    if not test_app_creation():
        print("\n❌ Application creation failed")
        return False

    print("\n✅ Installation test passed!")
    print("🚀 Ready to start: python3 run.py")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

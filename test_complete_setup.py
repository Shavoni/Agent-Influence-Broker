"""
Agent Influence Broker - Complete Setup Test

Tests all components to ensure proper integration and functionality.
"""

import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_complete_setup():
    """Test complete application setup."""

    print("🧪 Agent Influence Broker - Complete Setup Test")
    print("=" * 60)

    tests_passed = 0
    total_tests = 6

    # Test 1: Core imports
    print("📋 Test 1: Core imports...")
    try:
        from app.core.config import get_settings
        from app.core.logging import get_logger

        settings = get_settings()
        logger = get_logger(__name__)
        tests_passed += 1
        print("✅ Core imports successful")
    except Exception as e:
        print(f"❌ Core imports failed: {e}")

    # Test 2: Security module
    print("\n📋 Test 2: Security module...")
    try:
        from app.core.security import SecurityManager, get_current_user_id

        security = SecurityManager()
        tests_passed += 1
        print("✅ Security module imported")
    except Exception as e:
        print(f"❌ Security module failed: {e}")

    # Test 3: Database module
    print("\n📋 Test 3: Database connection...")
    try:
        from app.core.database import get_database_session, init_database

        tests_passed += 1
        print("✅ Database module imported")
    except Exception as e:
        print(f"❌ Database module failed: {e}")

    # Test 4: Models
    print("\n📋 Test 4: Database models...")
    try:
        from app.models.agent import Agent
        from app.models.user import User

        tests_passed += 1
        print("✅ Database models imported")
    except Exception as e:
        print(f"❌ Database models failed: {e}")

    # Test 5: Schemas
    print("\n📋 Test 5: Pydantic schemas...")
    try:
        from app.schemas.agent import AgentCreate, AgentResponse

        tests_passed += 1
        print("✅ Pydantic schemas imported")
    except Exception as e:
        print(f"❌ Pydantic schemas failed: {e}")

    # Test 6: Main application
    print("\n📋 Test 6: Main application...")
    try:
        from app.main import app

        tests_passed += 1
        print("✅ Main application imported")
        print(f"App title: {app.title}")
        print(f"App version: {app.version}")
    except Exception as e:
        print(f"❌ Main application failed: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"📈 Results: {tests_passed}/{total_tests} tests passed")

    if tests_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Agent Influence Broker setup complete")
        print("\n🚀 Ready to start:")
        print("   python3 run.py")
        return True
    else:
        print(f"\n⚠️ {total_tests - tests_passed} tests failed")
        print("🔧 Review errors and fix issues")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_complete_setup())
    sys.exit(0 if success else 1)

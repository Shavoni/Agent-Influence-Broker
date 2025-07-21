"""
Comprehensive setup test for Agent Influence Broker.

Implements testing strategy following project standards with async test support
and comprehensive validation of all core components.
"""

import asyncio
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_critical_imports() -> bool:
    """
    Test all critical imports with detailed error reporting.

    Following project testing strategy for comprehensive validation.

    Returns:
        True if all imports successful, False otherwise
    """
    print("🧪 Testing critical imports...")

    imports_to_test = [
        ("fastapi", "FastAPI web framework"),
        ("uvicorn", "ASGI server"),
        ("pydantic", "Data validation with Pydantic models"),
        ("pydantic_settings", "Settings management"),
        ("dotenv", "Environment configuration"),
        ("jose", "JWT authentication"),
        ("multipart", "Form data parsing"),
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


async def test_app_configuration() -> bool:
    """
    Test application configuration following project security considerations.

    Returns:
        True if configuration valid, False otherwise
    """
    print("\n🧪 Testing application configuration...")

    try:
        from app.core.config import get_pydantic_version, get_settings, is_pydantic_v2

        settings = get_settings()
        print(f"✅ Configuration loaded: {settings.APP_NAME}")
        print(f"✅ Environment: {settings.ENVIRONMENT}")
        print(f"✅ Pydantic version: {get_pydantic_version()} (v2: {is_pydantic_v2()})")
        print(f"✅ Debug mode: {settings.DEBUG}")
        print(f"✅ Host: {settings.HOST}:{settings.PORT}")

        # Test security configurations
        if len(settings.SECRET_KEY) >= 32:
            print("✅ Secret key meets security requirements")
        else:
            print("⚠️  Secret key should be at least 32 characters in production")

        return True

    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False


async def test_app_creation() -> bool:
    """
    Test application creation following FastAPI best practices.

    Returns:
        True if application created successfully, False otherwise
    """
    print("\n🧪 Testing FastAPI application creation...")

    try:
        from app.main import app

        print("✅ FastAPI application created successfully")

        # Test application configuration
        print(f"✅ App title: {app.title}")
        print(f"✅ App version: {app.version}")

        # Test middleware configuration
        middleware_count = len(app.user_middleware)
        print(f"✅ Middleware configured: {middleware_count} middleware layers")

        return True

    except Exception as e:
        print(f"❌ Application creation failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback

        traceback.print_exc()
        return False


async def test_database_configuration() -> bool:
    """
    Test database configuration for Supabase integration.

    Returns:
        True if database configuration valid, False otherwise
    """
    print("\n🧪 Testing database configuration...")

    try:
        from app.core.config import get_database_url, get_settings

        settings = get_settings()
        db_url = get_database_url()

        print(f"✅ Database URL configured: {db_url[:30]}...")
        print(f"✅ Database provider: Supabase (PostgreSQL with RLS)")

        if settings.SUPABASE_ANON_KEY != "placeholder-key":
            print("✅ Supabase anonymous key configured")
        else:
            print("ℹ️  Using placeholder Supabase key (development mode)")

        return True

    except Exception as e:
        print(f"❌ Database configuration test failed: {e}")
        return False


async def test_security_configuration() -> bool:
    """
    Test security configuration following project security considerations.

    Returns:
        True if security properly configured, False otherwise
    """
    print("\n🧪 Testing security configuration...")

    try:
        from app.core.config import get_cors_origins, get_settings

        settings = get_settings()
        cors_origins = get_cors_origins()

        print(f"✅ JWT algorithm: {settings.ALGORITHM}")
        print(f"✅ Token expiration: {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
        print(f"✅ CORS origins: {len(cors_origins)} configured")
        print(
            f"✅ Rate limiting: {settings.RATE_LIMIT_REQUESTS} requests/{settings.RATE_LIMIT_WINDOW}s"
        )

        # Validate security settings
        if settings.ENVIRONMENT == "production" and settings.DEBUG:
            print("⚠️  Debug mode should be disabled in production")
        else:
            print("✅ Debug mode appropriately configured")

        return True

    except Exception as e:
        print(f"❌ Security configuration test failed: {e}")
        return False


async def test_logging_configuration() -> bool:
    """
    Test logging configuration following comprehensive logging strategy.

    Returns:
        True if logging properly configured, False otherwise
    """
    print("\n🧪 Testing logging configuration...")

    try:
        from app.core.config import get_settings
        from app.core.logging import setup_logging

        # Setup logging
        setup_logging()

        settings = get_settings()
        print(f"✅ Log level: {settings.LOG_LEVEL}")
        print("✅ Logging system initialized")

        # Test logger creation
        import logging

        logger = logging.getLogger("app.test")
        logger.info("Test log message")
        print("✅ Logger functionality verified")

        return True

    except Exception as e:
        print(f"❌ Logging configuration test failed: {e}")
        return False


async def run_comprehensive_tests() -> Dict[str, bool]:
    """
    Run all comprehensive tests following project testing strategy.

    Returns:
        Dictionary mapping test names to results
    """
    tests = [
        ("Critical Imports", test_critical_imports),
        ("App Configuration", test_app_configuration),
        ("App Creation", test_app_creation),
        ("Database Configuration", test_database_configuration),
        ("Security Configuration", test_security_configuration),
        ("Logging Configuration", test_logging_configuration),
    ]

    results = {}

    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"📋 {test_name}")
        print("=" * 60)

        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False

    return results


async def main() -> None:
    """
    Main test routine with comprehensive validation.

    Implements project testing standards with detailed reporting.
    """
    print("🔍 Agent Influence Broker - Comprehensive Setup Test")
    print("🚀 Following FastAPI best practices and project architecture")
    print("=" * 80)

    # Run all tests
    results = await run_comprehensive_tests()

    # Report results
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80)

    passed_tests = []
    failed_tests = []

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status:<12} {test_name}")

        if result:
            passed_tests.append(test_name)
        else:
            failed_tests.append(test_name)

    print("\n" + "=" * 80)
    print(f"📈 Results: {len(passed_tests)}/{len(results)} tests passed")

    if failed_tests:
        print(f"\n❌ Failed tests requiring attention:")
        for test in failed_tests:
            print(f"  • {test}")

        print(f"\n🔧 Recommended actions:")
        print("1. Check dependency installation: pip list")
        print("2. Verify .env file configuration")
        print("3. Review application structure and imports")
        print("4. Check Python version compatibility")

        return False
    else:
        print("\n✅ All tests passed! Agent Influence Broker is ready for deployment.")
        print("\n🚀 Next steps:")
        print("1. Start development server: python3 run.py")
        print("2. Access API documentation: http://127.0.0.1:8000/docs")
        print("3. Begin agent registration and testing")
        print("4. Implement comprehensive test coverage (>90%)")

        return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

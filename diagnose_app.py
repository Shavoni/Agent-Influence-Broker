"""
Enhanced diagnostic test for Agent Influence Broker app creation.

Implements comprehensive error analysis following project testing strategy
with detailed FastAPI application debugging.
"""

import sys
import traceback
from pathlib import Path
from typing import Optional

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def diagnose_app_creation() -> bool:
    """
    Comprehensive diagnosis of app creation issues.

    Following project architecture standards for detailed error analysis.

    Returns:
        True if diagnosis successful, False otherwise
    """
    print("🔍 Diagnosing FastAPI Application Creation Issues")
    print("=" * 60)

    # Test 1: Check if main module exists
    print("📋 Step 1: Checking main module structure...")
    main_file = project_root / "app" / "main.py"

    if not main_file.exists():
        print("❌ app/main.py file not found")
        print("🔧 Creating basic FastAPI application structure...")
        await create_basic_app_structure()
        return False
    else:
        print("✅ app/main.py file exists")

    # Test 2: Check app directory structure
    print("\n📋 Step 2: Validating app directory structure...")
    required_files = [
        "app/__init__.py",
        "app/main.py",
        "app/core/__init__.py",
        "app/core/config.py",
        "app/core/logging.py",
    ]

    missing_files = []
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} missing")
            missing_files.append(file_path)

    if missing_files:
        print(f"\n🔧 Creating missing files: {', '.join(missing_files)}")
        await create_missing_files(missing_files)

    # Test 3: Try importing each component individually
    print("\n📋 Step 3: Testing individual component imports...")

    # Test config import
    try:
        from app.core.config import get_settings

        settings = get_settings()
        print("✅ Configuration import successful")
    except Exception as e:
        print(f"❌ Configuration import failed: {e}")
        traceback.print_exc()
        return False

    # Test logging import
    try:
        from app.core.logging import setup_logging

        print("✅ Logging import successful")
    except Exception as e:
        print(f"❌ Logging import failed: {e}")
        traceback.print_exc()
        return False

    # Test 4: Try creating FastAPI app step by step
    print("\n📋 Step 4: Testing FastAPI application creation...")

    try:
        import fastapi

        print(f"✅ FastAPI import successful (v{fastapi.__version__})")

        # Try basic app creation
        basic_app = fastapi.FastAPI(title="Test App")
        print("✅ Basic FastAPI app creation successful")

    except Exception as e:
        print(f"❌ Basic FastAPI app creation failed: {e}")
        traceback.print_exc()
        return False

    # Test 5: Try importing the actual app
    print("\n📋 Step 5: Testing actual app import...")

    try:
        from app.main import app

        print("✅ App import successful")
        print(f"✅ App type: {type(app)}")
        print(f"✅ App title: {getattr(app, 'title', 'Unknown')}")

        return True

    except Exception as e:
        print(f"❌ App import failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        print("\n🔍 Detailed error traceback:")
        traceback.print_exc()

        # Try to provide specific guidance based on error type
        await provide_error_guidance(e)

        return False


async def create_basic_app_structure() -> None:
    """
    Create basic app structure following project architecture.

    Implements FastAPI best practices with proper dependency injection.
    """
    print("🏗️  Creating basic app structure...")

    # Create app directory
    app_dir = project_root / "app"
    app_dir.mkdir(exist_ok=True)

    # Create core directory
    core_dir = app_dir / "core"
    core_dir.mkdir(exist_ok=True)

    # Create __init__.py files
    (app_dir / "__init__.py").touch()
    (core_dir / "__init__.py").touch()

    print("✅ Basic directory structure created")


async def create_missing_files(missing_files: list[str]) -> None:
    """
    Create missing files with basic content following project standards.

    Args:
        missing_files: List of missing file paths
    """
    for file_path in missing_files:
        full_path = project_root / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        if not full_path.exists():
            if file_path.endswith("__init__.py"):
                full_path.write_text('"""Package initialization."""\n')
            else:
                full_path.touch()

        print(f"✅ Created {file_path}")


async def provide_error_guidance(error: Exception) -> None:
    """
    Provide specific guidance based on error type.

    Args:
        error: The exception that occurred
    """
    error_type = type(error).__name__
    error_message = str(error)

    print(f"\n💡 Error Analysis for {error_type}:")

    if "ModuleNotFoundError" in error_type:
        if "app.core" in error_message:
            print("🔧 Missing app.core module - creating basic structure")
        elif "fastapi" in error_message:
            print("🔧 FastAPI not installed - run: pip install fastapi")
        else:
            print("🔧 Missing dependency - check imports and installation")

    elif "ImportError" in error_type:
        print("🔧 Import error - check module structure and dependencies")

    elif "AttributeError" in error_type:
        print("🔧 Attribute error - check configuration and object creation")

    elif "ValidationError" in error_type:
        print("🔧 Pydantic validation error - check environment configuration")

    else:
        print("🔧 Unexpected error - check full traceback above")


async def main() -> None:
    """
    Main diagnostic routine following project testing standards.
    """
    print("🚨 Agent Influence Broker - App Creation Diagnosis")
    print("Following FastAPI best practices and project architecture")
    print("=" * 80)

    success = await diagnose_app_creation()

    if success:
        print("\n✅ Diagnosis complete - app creation should work now")
        print("🚀 Try running: python3 test_setup_complete.py")
    else:
        print("\n❌ Issues found that need resolution")
        print("🔧 Follow the guidance above to fix the problems")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

#!/usr/bin/env python3
"""
Agent Influence Broker - Status Verification

Comprehensive check of current setup status following project architecture
and determining next steps for sophisticated FastAPI implementation.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List


async def verify_agent_broker_status() -> Dict[str, Any]:
    """
    Comprehensive status check following project architecture standards.

    Returns:
        Dict containing detailed status of all components
    """

    status = {
        "core_components": {},
        "dependencies": {},
        "architecture": {},
        "next_steps": [],
        "overall_health": "unknown",
    }

    print("🔍 Agent Influence Broker - Comprehensive Status Check")
    print("=" * 55)

    # Check 1: Core Configuration and Logging
    print("\n📋 Checking Core Components...")
    try:
        from app.core.config import get_settings
        from app.core.logging import get_logger

        settings = get_settings()
        logger = get_logger(__name__)

        # Test LOG_LEVEL access specifically
        log_level = settings.LOG_LEVEL

        status["core_components"]["config"] = "✅ Working"
        status["core_components"]["logging"] = "✅ Working"
        status["core_components"]["log_level_fix"] = "✅ Fixed"

        logger.info("Core components verification successful")
        print("✅ Configuration and Logging: Working")

    except Exception as e:
        status["core_components"]["error"] = str(e)
        print(f"❌ Core components error: {e}")
        return status

    # Check 2: FastAPI Dependencies
    print("\n📋 Checking FastAPI Stack...")
    try:
        import fastapi
        import uvicorn

        status["dependencies"]["fastapi"] = f"✅ {fastapi.__version__}"
        status["dependencies"]["uvicorn"] = f"✅ {uvicorn.__version__}"
        print(f"✅ FastAPI: {fastapi.__version__}")
        print(f"✅ Uvicorn: {uvicorn.__version__}")

    except ImportError as e:
        status["dependencies"]["fastapi_error"] = str(e)
        print(f"❌ FastAPI stack missing: {e}")
        status["next_steps"].append("Install FastAPI dependencies")

    # Check 3: Application Structure
    print("\n📋 Checking Application Architecture...")
    required_structure = [
        "app/__init__.py",
        "app/core/config.py",
        "app/core/logging.py",
        "app/main.py",
    ]

    structure_complete = True
    for file_path in required_structure:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            structure_complete = False
            status["next_steps"].append(f"Create {file_path}")

    status["architecture"]["structure_complete"] = structure_complete

    # Check 4: Database Capabilities
    print("\n📋 Checking Database Integration...")
    try:
        import sqlalchemy

        status["dependencies"]["sqlalchemy"] = f"✅ {sqlalchemy.__version__}"
        print(f"✅ SQLAlchemy: {sqlalchemy.__version__}")

        try:
            import aiosqlite

            status["dependencies"]["aiosqlite"] = f"✅ {aiosqlite.__version__}"
            print(f"✅ AIOSQLite: {aiosqlite.__version__}")
        except ImportError:
            print("⚠️  AIOSQLite not available - database features limited")
            status["next_steps"].append("Install aiosqlite for async database support")

    except ImportError:
        print("❌ Database packages not available")
        status["next_steps"].append(
            "Install database dependencies (SQLAlchemy + aiosqlite)"
        )

    # Check 5: Authentication Readiness
    print("\n📋 Checking Authentication Components...")
    auth_components = ["python-jose", "passlib", "cryptography"]
    auth_ready = True

    for component in auth_components:
        try:
            if component == "python-jose":
                import jose

                status["dependencies"]["jose"] = "✅ Available"
                print("✅ Python-JOSE: Available")
            elif component == "passlib":
                import passlib

                status["dependencies"]["passlib"] = "✅ Available"
                print("✅ Passlib: Available")
            elif component == "cryptography":
                import cryptography

                status["dependencies"]["cryptography"] = "✅ Available"
                print("✅ Cryptography: Available")
        except ImportError:
            print(f"⚠️  {component}: Not available")
            auth_ready = False

    if not auth_ready:
        status["next_steps"].append(
            "Install authentication dependencies for JWT support"
        )

    # Check 6: Main Application
    print("\n📋 Checking Main Application...")
    try:
        if Path("app/main.py").exists():
            from app.main import app

            status["architecture"]["main_app"] = "✅ Available"
            print(f"✅ Main FastAPI app: {app.title}")
        else:
            status["next_steps"].append("Create main FastAPI application")
            print("❌ Main application not found")
    except Exception as e:
        print(f"⚠️  Main application error: {e}")
        status["next_steps"].append("Fix main application issues")

    # Determine overall health
    if not status["next_steps"]:
        status["overall_health"] = "excellent"
        print("\n🎉 Status: Excellent - Ready for advanced development!")
    elif len(status["next_steps"]) <= 2:
        status["overall_health"] = "good"
        print("\n✅ Status: Good - Minor components needed")
    else:
        status["overall_health"] = "needs_work"
        print("\n⚠️  Status: Needs work - Several components missing")

    return status


def print_next_steps(status: Dict[str, Any]) -> None:
    """Print recommended next steps based on status."""

    if status["overall_health"] == "excellent":
        print("\n🚀 Ready for Next Phase - Advanced Features:")
        print("=" * 45)
        print("1. 🤖 Implement Agent Management endpoints")
        print("2. ⚡ Build Negotiation Engine core logic")
        print("3. 📊 Add Influence Metrics calculation")
        print("4. 💰 Create Transaction System")
        print("5. 🔗 Implement Webhook notifications")
        print("6. 🔐 Add JWT authentication middleware")
        print("7. 🧪 Expand test coverage")

    elif status["overall_health"] == "good":
        print("\n🔧 Complete These Steps First:")
        print("=" * 30)
        for i, step in enumerate(status["next_steps"], 1):
            print(f"{i}. {step}")

        print("\n💡 Quick Setup Commands:")
        if "Install database dependencies" in str(status["next_steps"]):
            print("pip install sqlalchemy>=2.0.25 aiosqlite>=0.19.0")
        if "Install authentication dependencies" in str(status["next_steps"]):
            print("pip install python-jose[cryptography] passlib[bcrypt]")

    else:
        print("\n🛠️  Major Components Needed:")
        print("=" * 28)
        for i, step in enumerate(status["next_steps"], 1):
            print(f"{i}. {step}")

        print("\n💡 Consider running the phase setup scripts in order")


async def main():
    """Main verification execution."""

    try:
        status = await verify_agent_broker_status()
        print_next_steps(status)

        # Create status report file
        status_file = Path("agent_broker_status.json")
        import json

        with open(status_file, "w") as f:
            json.dump(status, f, indent=2)

        print(f"\n📄 Status report saved to: {status_file}")

        return status["overall_health"] in ["excellent", "good"]

    except Exception as e:
        print(f"❌ Status check failed: {e}")
        return False


if __name__ == "__main__":
    import asyncio

    success = asyncio.run(main())

    if success:
        print("\n🎊 Agent Influence Broker status check complete!")
    else:
        print("\n⚠️  Issues found - please address before proceeding")

#!/usr/bin/env python3
"""
Agent Influence Broker - Phase 1: Core Foundation Setup

Establishes the fundamental FastAPI application structure following
project architecture and security considerations.
"""

import subprocess
import sys
from pathlib import Path


def setup_core_foundation():
    """Setup core foundation with minimal dependencies."""

    print("🚀 Phase 1: Core Foundation Setup")
    print("=" * 40)

    # Step 1: Install absolute essentials
    core_packages = [
        "fastapi==0.104.1",
        "uvicorn==0.24.0",  # Basic uvicorn without extras
        "python-dotenv==1.0.0",
        "httpx==0.25.2",
    ]

    print("📦 Installing core FastAPI essentials...")
    for package in core_packages:
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                check=True,
                capture_output=True,
            )
            print(f"✅ {package}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed: {package}")
            return False

    # Step 2: Create minimal app structure
    create_minimal_structure()

    # Step 3: Test basic functionality
    if test_basic_setup():
        print("✅ Phase 1 Complete - Core foundation ready")
        return True
    else:
        print("❌ Phase 1 Failed")
        return False


def create_minimal_structure():
    """Create minimal application structure."""

    # Basic app structure
    app_dir = Path("app")
    app_dir.mkdir(exist_ok=True)

    # Minimal __init__.py
    (app_dir / "__init__.py").write_text(
        '''
"""Agent Influence Broker - Core Package"""
__version__ = "1.0.0"
'''
    )

    # Basic main.py
    (app_dir / "main.py").write_text(
        '''
"""Agent Influence Broker - Basic FastAPI App"""

from fastapi import FastAPI

app = FastAPI(
    title="Agent Influence Broker",
    version="1.0.0",
    description="AI agent negotiation platform"
)

@app.get("/")
async def root():
    return {"message": "Agent Influence Broker - Phase 1 Active"}

@app.get("/health")
async def health():
    return {"status": "healthy", "phase": "foundation"}
'''
    )

    print("✅ Minimal structure created")


def test_basic_setup():
    """Test that basic setup works."""
    try:
        import fastapi
        import uvicorn

        from app.main import app

        print("✅ Basic imports successful")
        return True
    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        return False


if __name__ == "__main__":
    setup_core_foundation()

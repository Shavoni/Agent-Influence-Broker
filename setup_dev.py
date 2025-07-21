#!/usr/bin/env python3
"""
Development setup script for Agent Influence Broker.

Implements comprehensive dependency installation with wheel build fixes,
following the project's architecture and security standards.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

# Project root configuration
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class DependencyManager:
    """
    Manages dependency installation with comprehensive error handling.

    Implements best practices for Python package management and
    handles common installation issues across different platforms.
    """

    def __init__(self):
        """Initialize dependency manager with platform detection."""
        self.platform = platform.system().lower()
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        self.is_macos = self.platform == "darwin"
        self.is_apple_silicon = self.is_macos and platform.machine() == "arm64"

    def check_system_requirements(self) -> bool:
        """
        Check system requirements and dependencies.

        Returns:
            True if system requirements are met, False otherwise
        """
        print("🔍 Checking system requirements...")

        # Check Python version
        if sys.version_info < (3, 8):
            print(f"❌ Python 3.8+ required, found {self.python_version}")
            return False
        print(f"✅ Python {self.python_version}")

        # Check pip availability
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                check=True,
                capture_output=True,
            )
            print("✅ pip available")
        except subprocess.CalledProcessError:
            print("❌ pip not available")
            return False

        # Check for development tools on macOS
        if self.is_macos:
            if not self._check_xcode_tools():
                print("⚠️  Xcode command line tools recommended for building packages")

        return True

    def _check_xcode_tools(self) -> bool:
        """Check if Xcode command line tools are installed."""
        try:
            subprocess.run(
                ["xcode-select", "--print-path"], check=True, capture_output=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def upgrade_pip_and_tools(self) -> bool:
        """
        Upgrade pip and essential build tools.

        Returns:
            True if upgrade successful, False otherwise
        """
        print("🔧 Upgrading pip and build tools...")

        upgrade_commands = [
            # Upgrade pip first
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
            # Install/upgrade build tools
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--upgrade",
                "setuptools",
                "wheel",
            ],
            # Install build dependencies for problematic packages
            [sys.executable, "-m", "pip", "install", "--upgrade", "Cython"],
        ]

        for cmd in upgrade_commands:
            try:
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                print(f"✅ {' '.join(cmd[4:])}")
            except subprocess.CalledProcessError as e:
                print(f"⚠️  Warning: {' '.join(cmd[4:])} failed: {e.stderr}")
                # Continue anyway as these might not be critical

        return True

    def install_core_dependencies(self) -> bool:
        """
        Install core dependencies with fallback strategies.

        Returns:
            True if installation successful, False otherwise
        """
        print("📦 Installing core dependencies...")

        # Core dependencies in order of installation priority
        core_deps = [
            # Essential framework components
            ("fastapi", "0.104.1", "FastAPI web framework"),
            ("uvicorn[standard]", "0.24.0", "ASGI server"),
            ("python-dotenv", "1.0.0", "Environment configuration"),
            # Data validation (with specific version to avoid wheel issues)
            ("pydantic", "2.4.2", "Data validation"),
            # Authentication
            ("python-jose[cryptography]", "3.3.0", "JWT authentication"),
            ("python-multipart", "0.0.6", "Form data parsing"),
            # HTTP client
            ("httpx", "0.25.2", "HTTP client"),
        ]

        failed_packages = []

        for package, version, description in core_deps:
            if not self._install_package(package, version, description):
                failed_packages.append(package)

        if failed_packages:
            print(f"\n❌ Failed to install: {', '.join(failed_packages)}")
            return False

        print("✅ Core dependencies installed successfully")
        return True

    def _install_package(self, package: str, version: str, description: str) -> bool:
        """
        Install a single package with multiple fallback strategies.

        Args:
            package: Package name
            version: Package version
            description: Human-readable description

        Returns:
            True if installation successful, False otherwise
        """
        package_spec = f"{package}=={version}" if version else package

        print(f"  Installing {package} ({description})...")

        # Strategy 1: Normal installation
        if self._try_install_command(
            [sys.executable, "-m", "pip", "install", package_spec]
        ):
            return True

        # Strategy 2: Use pre-compiled wheels only
        print(f"    Retrying with wheels only...")
        if self._try_install_command(
            [sys.executable, "-m", "pip", "install", "--only-binary=all", package_spec]
        ):
            return True

        # Strategy 3: Install without version constraint
        if version:
            print(f"    Retrying without version constraint...")
            if self._try_install_command(
                [sys.executable, "-m", "pip", "install", package]
            ):
                return True

        # Strategy 4: Use conda if available (for problematic packages)
        if package == "pydantic" and self._has_conda():
            print(f"    Trying conda installation...")
            if self._try_install_command(
                ["conda", "install", "-c", "conda-forge", package, "-y"]
            ):
                return True

        return False

    def _try_install_command(self, cmd: List[str]) -> bool:
        """Execute installation command with error handling."""
        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            # Log error but don't print to keep output clean
            return False

    def _has_conda(self) -> bool:
        """Check if conda is available."""
        try:
            subprocess.run(["conda", "--version"], check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def verify_installation(self) -> bool:
        """
        Verify that all critical packages are importable.

        Returns:
            True if verification successful, False otherwise
        """
        print("🧪 Verifying installation...")

        critical_imports = [
            ("fastapi", "FastAPI framework"),
            ("uvicorn", "ASGI server"),
            ("pydantic", "Data validation"),
            ("dotenv", "Environment config"),
        ]

        failed_imports = []

        for module, description in critical_imports:
            try:
                __import__(module)
                print(f"✅ {module} ({description})")
            except ImportError:
                print(f"❌ {module} ({description})")
                failed_imports.append(module)

        return len(failed_imports) == 0

    def create_environment_file(self) -> bool:
        """
        Create default environment configuration file.

        Returns:
            True if file created successfully, False otherwise
        """
        env_file = project_root / ".env"

        if env_file.exists():
            print("✅ .env file already exists")
            return True

        print("📝 Creating default .env file...")

        env_content = """# Agent Influence Broker - Environment Configuration
# Following security best practices and project architecture

# Application Settings
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

# Webhook Configuration (for future use)
WEBHOOK_SECRET=dev-webhook-secret
"""

        try:
            env_file.write_text(env_content)
            print("✅ .env file created")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False


def main() -> None:
    """
    Main setup routine following project architecture standards.

    Implements comprehensive dependency installation with error recovery
    and detailed progress reporting.
    """
    print("🚀 Agent Influence Broker - Development Setup")
    print("=" * 60)
    print(f"Platform: {platform.system()} {platform.machine()}")
    print(f"Python: {sys.version}")
    print("=" * 60)

    # Initialize dependency manager
    dep_manager = DependencyManager()

    # Run setup steps
    setup_steps = [
        ("System Requirements", dep_manager.check_system_requirements),
        ("Upgrade Build Tools", dep_manager.upgrade_pip_and_tools),
        ("Install Dependencies", dep_manager.install_core_dependencies),
        ("Verify Installation", dep_manager.verify_installation),
        ("Create Environment", dep_manager.create_environment_file),
    ]

    failed_steps = []

    for step_name, step_func in setup_steps:
        print(f"\n📋 {step_name}:")
        try:
            if not step_func():
                failed_steps.append(step_name)
        except Exception as e:
            print(f"❌ {step_name} failed with exception: {e}")
            failed_steps.append(step_name)

    # Report results
    print("\n" + "=" * 60)
    if failed_steps:
        print(f"❌ Setup incomplete. Failed steps: {', '.join(failed_steps)}")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure you have Python 3.8+ installed")
        print("2. On macOS, install Xcode command line tools: xcode-select --install")
        print("3. Try upgrading pip: python3 -m pip install --upgrade pip")
        print("4. For Apple Silicon Macs, consider using conda or miniforge")
        print("5. Run this script again after resolving issues")
        sys.exit(1)
    else:
        print("✅ Setup completed successfully!")
        print("\n🚀 Next steps:")
        print("1. Run the application: python3 run.py")
        print("2. Visit API docs: http://127.0.0.1:8000/docs")
        print("3. Check health endpoint: http://127.0.0.1:8000/health")


if __name__ == "__main__":
    main()

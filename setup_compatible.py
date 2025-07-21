"""
Enhanced compatibility setup for Agent Influence Broker.

Implements version-aware dependency management following the project's
architecture standards and security considerations.
"""

import platform
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Project root configuration
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class CompatibilityManager:
    """
    Manages Python version compatibility and dependency resolution.

    Implements comprehensive version checking and dependency management
    following FastAPI best practices and security considerations.
    """

    def __init__(self):
        """Initialize compatibility manager with version detection."""
        self.python_version = sys.version_info
        self.python_version_str = (
            f"{self.python_version.major}.{self.python_version.minor}"
        )
        self.is_python_313_plus = self.python_version >= (3, 13)
        self.platform = platform.system().lower()

    def get_compatible_dependencies(self) -> Dict[str, str]:
        """
        Get compatible dependency versions based on Python version.

        Returns:
            Dictionary mapping package names to compatible versions
        """
        if self.is_python_313_plus:
            # Python 3.13+ compatible versions
            return {
                "fastapi": "0.104.1",
                "uvicorn[standard]": "0.24.0",
                "pydantic": "2.5.0",  # Use newer pydantic for Python 3.13
                "pydantic-settings": "2.1.0",
                "python-dotenv": "1.0.0",
                "python-jose[cryptography]": "3.3.0",
                "python-multipart": "0.0.6",
                "httpx": "0.25.2",
                "passlib[bcrypt]": "1.7.4",
            }
        else:
            # Python 3.8-3.12 compatible versions
            return {
                "fastapi": "0.104.1",
                "uvicorn[standard]": "0.24.0",
                "pydantic": "1.10.12",
                "python-dotenv": "1.0.0",
                "python-jose[cryptography]": "3.3.0",
                "python-multipart": "0.0.6",
                "httpx": "0.25.2",
                "passlib[bcrypt]": "1.7.4",
            }

    def clean_existing_installation(self) -> bool:
        """
        Clean existing problematic installations.

        Returns:
            True if cleaning successful, False otherwise
        """
        print("🧹 Cleaning existing installations...")

        # Packages that commonly cause conflicts
        conflicting_packages = [
            "pydantic",
            "pydantic-core",
            "pydantic-settings",
            "realtime",  # Supabase realtime that has strict pydantic requirements
        ]

        for package in conflicting_packages:
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "uninstall", package, "-y"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    print(f"✅ Uninstalled {package}")
                else:
                    print(f"ℹ️  {package} not found (skipping)")
            except Exception as e:
                print(f"⚠️  Warning cleaning {package}: {e}")

        return True

    def install_compatible_dependencies(self) -> bool:
        """
        Install compatible dependencies in correct order.

        Returns:
            True if installation successful, False otherwise
        """
        print(f"📦 Installing dependencies for Python {self.python_version_str}...")

        compatible_deps = self.get_compatible_dependencies()

        # Installation order matters for compatibility
        install_order = [
            "python-dotenv",  # Environment first
            "pydantic",  # Core validation
            "pydantic-settings" if self.is_python_313_plus else None,
            "fastapi",  # Web framework
            "uvicorn[standard]",  # ASGI server
            "python-jose[cryptography]",  # Authentication
            "python-multipart",  # Form handling
            "httpx",  # HTTP client
            "passlib[bcrypt]",  # Password hashing
        ]

        # Filter out None values
        install_order = [pkg for pkg in install_order if pkg is not None]

        failed_packages = []

        for package in install_order:
            if package in compatible_deps:
                version = compatible_deps[package]
                if not self._install_single_package(package, version):
                    failed_packages.append(package)
            else:
                if not self._install_single_package(package, None):
                    failed_packages.append(package)

        if failed_packages:
            print(f"❌ Failed to install: {', '.join(failed_packages)}")
            return False

        print("✅ All dependencies installed successfully")
        return True

    def _install_single_package(self, package: str, version: Optional[str]) -> bool:
        """
        Install a single package with error handling.

        Args:
            package: Package name
            version: Package version (optional)

        Returns:
            True if installation successful, False otherwise
        """
        package_spec = f"{package}=={version}" if version else package
        print(f"  Installing {package_spec}...")

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package_spec],
                check=True,
                capture_output=True,
                text=True,
                timeout=300,
            )
            print(f"    ✅ {package}")
            return True

        except subprocess.CalledProcessError as e:
            print(f"    ❌ {package}: {e.stderr}")
            return False
        except subprocess.TimeoutExpired:
            print(f"    ❌ {package}: Installation timeout")
            return False

    def verify_installation(self) -> bool:
        """
        Verify that all packages are properly installed and importable.

        Returns:
            True if verification successful, False otherwise
        """
        print("🧪 Verifying installation...")

        # Test critical imports
        test_imports = [
            ("fastapi", "FastAPI web framework"),
            ("uvicorn", "ASGI server"),
            ("pydantic", "Data validation"),
            ("dotenv", "Environment configuration"),
        ]

        all_passed = True

        for module, description in test_imports:
            try:
                imported = __import__(module)
                version = getattr(imported, "__version__", "unknown")
                print(f"✅ {module} v{version} - {description}")
            except ImportError as e:
                print(f"❌ {module} - {description}: {e}")
                all_passed = False

        return all_passed

    def test_application_imports(self) -> bool:
        """
        Test application-specific imports following project structure.

        Returns:
            True if application imports successful, False otherwise
        """
        print("\n🧪 Testing application imports...")

        try:
            from app.core.config import get_settings

            settings = get_settings()
            print(f"✅ Configuration: {settings.APP_NAME}")

            from app.main import app

            print("✅ FastAPI application created")

            return True

        except Exception as e:
            print(f"❌ Application imports failed: {e}")
            print(f"   Error type: {type(e).__name__}")
            return False


def main() -> None:
    """
    Main compatibility setup routine.

    Implements comprehensive dependency management following
    the project's architecture and security standards.
    """
    print("🔧 Agent Influence Broker - Compatibility Setup")
    print("=" * 60)
    print(f"Python Version: {sys.version}")
    print(f"Platform: {platform.system()} {platform.machine()}")
    print("=" * 60)

    # Initialize compatibility manager
    compat_manager = CompatibilityManager()

    # Check Python version compatibility
    if compat_manager.python_version < (3, 8):
        print("❌ Python 3.8+ required for this project")
        sys.exit(1)

    if compat_manager.is_python_313_plus:
        print("ℹ️  Detected Python 3.13+ - using compatible dependency versions")

    # Run setup steps
    setup_steps = [
        ("Clean Existing Installation", compat_manager.clean_existing_installation),
        (
            "Install Compatible Dependencies",
            compat_manager.install_compatible_dependencies,
        ),
        ("Verify Installation", compat_manager.verify_installation),
        ("Test Application Imports", compat_manager.test_application_imports),
    ]

    failed_steps = []

    for step_name, step_func in setup_steps:
        print(f"\n📋 {step_name}:")
        try:
            if not step_func():
                failed_steps.append(step_name)
        except Exception as e:
            print(f"❌ {step_name} failed: {e}")
            failed_steps.append(step_name)

    # Report results
    print("\n" + "=" * 60)
    if failed_steps:
        print(f"❌ Setup failed. Issues with: {', '.join(failed_steps)}")
        print("\n🔧 Troubleshooting recommendations:")
        print("1. Ensure Python 3.8-3.12 for best compatibility")
        print("2. Consider using pyenv to manage Python versions")
        print("3. Create a fresh virtual environment")
        print("4. Check for system-level package conflicts")
        sys.exit(1)
    else:
        print("✅ Compatibility setup completed successfully!")
        print("\n🚀 Next steps:")
        print("1. Start the application: python3 run.py")
        print("2. Visit API documentation: http://127.0.0.1:8000/docs")
        print("3. Check application health: http://127.0.0.1:8000/health")


if __name__ == "__main__":
    main()

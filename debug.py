"""
Debug script to check environment and application setup
"""

import sys
import os
import importlib.util

def check_module(module_name):
    """Check if a module can be imported"""
    try:
        importlib.import_module(module_name)
        return f"✓ {module_name} is installed"
    except ImportError:
        return f"✗ {module_name} is NOT installed"

def main():
    """Main debug function"""
    print("=== Python Environment ===")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Working directory: {os.getcwd()}")
    
    print("\n=== Required Packages ===")
    modules = ["fastapi", "uvicorn", "pytest", "sqlalchemy", "httpx", 
               "aiosqlite", "supabase", "pydantic"]
    for module in modules:
        print(check_module(module))
    
    print("\n=== Application Structure ===")
    try:
        from src.app.main import app
        print("✓ FastAPI app can be imported")
        
        routes = [
            {"path": route.path, "name": route.name, "methods": route.methods}
            for route in app.routes
        ]
        print(f"Number of routes: {len(routes)}")
        for route in routes[:5]:  # Show first 5 routes
            print(f"  {route['path']} - {route['methods']}")
        
    except Exception as e:
        print(f"✗ Error importing FastAPI app: {str(e)}")
    
    print("\n=== Database Connection ===")
    try:
        from src.app.core.config import settings
        print(f"Database URL defined: {'DATABASE_URL' in dir(settings)}")
        
        # Try to connect to database but don't print connection string for security
        try:
            from src.app.core.database import get_db_session, Base
            print("✓ Database module can be imported")
        except Exception as db_error:
            print(f"✗ Database error: {str(db_error)}")
            
    except Exception as e:
        print(f"✗ Config error: {str(e)}")

if __name__ == "__main__":
    main()

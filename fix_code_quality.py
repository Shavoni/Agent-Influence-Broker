#!/usr/bin/env python3
"""
Code Quality Cleanup Tool for Agent Influence Broker

Automatically fixes common linting and formatting issues:
- Line length violations
- Blank lines with whitespace  
- Unused imports
- Trailing whitespace
- Import organization
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Set

def run_command(cmd: List[str]) -> tuple[bool, str, str]:
    """Run command and return success, stdout, stderr."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def install_tools():
    """Install required code quality tools."""
    print("📦 Installing code quality tools...")
    tools = ["black", "isort", "autoflake", "autopep8"]
    
    for tool in tools:
        print(f"   Installing {tool}...")
        success, stdout, stderr = run_command([sys.executable, "-m", "pip", "install", tool])
        if not success:
            print(f"   ⚠️ Failed to install {tool}: {stderr}")
        else:
            print(f"   ✅ {tool} installed")

def remove_unused_imports(file_path: str) -> bool:
    """Remove unused imports using autoflake."""
    print(f"🧹 Removing unused imports: {file_path}")
    
    success, stdout, stderr = run_command([
        "autoflake", 
        "--remove-all-unused-imports",
        "--remove-unused-variables", 
        "--in-place",
        file_path
    ])
    
    if not success:
        print(f"   ⚠️ Autoflake failed: {stderr}")
        return False
    
    print(f"   ✅ Cleaned unused imports")
    return True

def format_with_black(file_path: str) -> bool:
    """Format code with Black."""
    print(f"🎨 Formatting with Black: {file_path}")
    
    success, stdout, stderr = run_command([
        "black", 
        "--line-length", "79",
        "--target-version", "py311",
        file_path
    ])
    
    if not success:
        print(f"   ⚠️ Black formatting failed: {stderr}")
        return False
    
    print(f"   ✅ Black formatting complete")
    return True

def sort_imports(file_path: str) -> bool:
    """Sort imports with isort."""
    print(f"📚 Sorting imports: {file_path}")
    
    success, stdout, stderr = run_command([
        "isort",
        "--profile", "black",
        "--line-length", "79", 
        "--multi-line", "3",
        "--trailing-comma",
        "--force-grid-wrap", "0",
        "--combine-as",
        "--use-parentheses",
        file_path
    ])
    
    if not success:
        print(f"   ⚠️ isort failed: {stderr}")
        return False
    
    print(f"   ✅ Import sorting complete")
    return True

def clean_whitespace(file_path: str) -> bool:
    """Clean whitespace issues manually."""
    print(f"🧽 Cleaning whitespace: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove trailing whitespace
        lines = content.splitlines()
        cleaned_lines = [line.rstrip() for line in lines]
        
        # Remove empty lines with whitespace
        final_lines = []
        for line in cleaned_lines:
            if line.strip() == "":
                final_lines.append("")  # Keep empty line but no whitespace
            else:
                final_lines.append(line)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(final_lines) + '\n')
        
        print(f"   ✅ Whitespace cleaned")
        return True
        
    except Exception as e:
        print(f"   ⚠️ Whitespace cleaning failed: {e}")
        return False

def fix_long_lines(file_path: str) -> bool:
    """Fix long lines using autopep8."""
    print(f"📏 Fixing long lines: {file_path}")
    
    success, stdout, stderr = run_command([
        "autopep8", 
        "--in-place",
        "--max-line-length", "79",
        "--aggressive",
        "--aggressive",
        file_path
    ])
    
    if not success:
        print(f"   ⚠️ autopep8 failed: {stderr}")
        return False
    
    print(f"   ✅ Long lines fixed")
    return True

def get_python_files(directory: str) -> List[str]:
    """Get all Python files in directory."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.venv', 'venv', '.mypy_cache']]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return python_files

def process_file(file_path: str) -> dict:
    """Process a single Python file."""
    print(f"\n🔧 Processing: {file_path}")
    print("=" * 60)
    
    results = {
        "file": file_path,
        "success": True,
        "steps": []
    }
    
    steps = [
        ("clean_whitespace", clean_whitespace),
        ("remove_unused_imports", remove_unused_imports),
        ("fix_long_lines", fix_long_lines),
        ("sort_imports", sort_imports),
        ("format_with_black", format_with_black),
    ]
    
    for step_name, step_func in steps:
        try:
            success = step_func(file_path)
            results["steps"].append({
                "step": step_name,
                "success": success
            })
            if not success:
                results["success"] = False
        except Exception as e:
            print(f"   ❌ {step_name} failed: {e}")
            results["steps"].append({
                "step": step_name,
                "success": False,
                "error": str(e)
            })
            results["success"] = False
    
    if results["success"]:
        print(f"   🎉 {file_path} processing complete!")
    else:
        print(f"   ⚠️ {file_path} had some issues")
    
    return results

def main():
    """Main cleanup process."""
    print("🔧 Agent Influence Broker - Code Quality Cleanup")
    print("=" * 60)
    
    # Install tools first
    install_tools()
    
    # Get all Python files
    directories = ["app", "src"]  # Process both app and src directories
    all_files = []
    
    for directory in directories:
        if os.path.exists(directory):
            files = get_python_files(directory)
            all_files.extend(files)
            print(f"📁 Found {len(files)} Python files in {directory}/")
    
    if not all_files:
        print("❌ No Python files found to process")
        return
    
    print(f"📊 Total files to process: {len(all_files)}")
    print("")
    
    # Process each file
    results = []
    successful = 0
    
    for file_path in all_files:
        result = process_file(file_path)
        results.append(result)
        if result["success"]:
            successful += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("🏁 CLEANUP SUMMARY")
    print("=" * 60)
    print(f"📁 Total files processed: {len(all_files)}")
    print(f"✅ Successfully cleaned: {successful}")
    print(f"⚠️ Had issues: {len(all_files) - successful}")
    
    if successful == len(all_files):
        print("\n🎉 ALL FILES SUCCESSFULLY CLEANED!")
        print("Your code quality issues should now be resolved.")
    else:
        print(f"\n⚠️ {len(all_files) - successful} files had issues.")
        print("Check the output above for details.")
    
    # Show failed files
    failed_files = [r for r in results if not r["success"]]
    if failed_files:
        print("\n❌ Files with issues:")
        for result in failed_files:
            print(f"   - {result['file']}")
    
    print("\n🎯 Next steps:")
    print("1. Run the validation script to check remaining issues")
    print("2. Commit your cleaned code")
    print("3. Continue with feature development!")

if __name__ == "__main__":
    main()

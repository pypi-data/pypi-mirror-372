#!/usr/bin/env python3
"""
Script to build and upload the ASI1 MCP CLI package to PyPI.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return None

def main():
    """Main build and upload process."""
    print("🚀 ASI1 MCP CLI - PyPI Build and Upload")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Error: pyproject.toml not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Clean previous builds
    print("🧹 Cleaning previous builds...")
    run_command("rm -rf dist/ build/ *.egg-info/", "Cleaning build artifacts")
    
    # Install build dependencies
    print("📦 Installing build dependencies...")
    run_command("pip install build twine", "Installing build tools")
    
    # Build the package
    print("🔨 Building package...")
    build_output = run_command("python3 -m build", "Building package")
    if not build_output:
        sys.exit(1)
    
    # Check the built package
    print("🔍 Checking built package...")
    check_output = run_command("twine check dist/*", "Checking package")
    if not check_output:
        sys.exit(1)
    
    print("\n📋 Package built successfully!")
    print("📁 Built files:")
    for file in Path("dist").glob("*"):
        print(f"   - {file}")
    
    print("\n🚀 To upload to PyPI:")
    print("1. Test upload to TestPyPI:")
    print("   twine upload --repository testpypi dist/*")
    print("\n2. Upload to PyPI (production):")
    print("   twine upload dist/*")
    
    print("\n💡 Note: You'll need to:")
    print("- Have a PyPI account")
    print("- Configure your credentials (~/.pypirc)")
    print("- Update the version in pyproject.toml before uploading")

if __name__ == "__main__":
    main() 
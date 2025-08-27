#!/usr/bin/env python3
"""
Upload TNSA API package to PyPI
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"Error: {e.stderr}")
        return False


def clean_build():
    """Clean previous build artifacts."""
    print("\n🧹 Cleaning previous builds...")
    
    dirs_to_clean = ["build", "dist", "*.egg-info"]
    for pattern in dirs_to_clean:
        if pattern == "*.egg-info":
            # Find and remove .egg-info directories
            for path in Path(".").glob("*.egg-info"):
                if path.is_dir():
                    shutil.rmtree(path)
                    print(f"  Removed: {path}")
        else:
            path = Path(pattern)
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                print(f"  Removed: {path}")
    
    print("✅ Build cleanup completed!")


def check_requirements():
    """Check if required tools are installed."""
    print("\n🔍 Checking requirements...")
    
    required_packages = ["build", "twine"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package} is missing")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        install_cmd = f"{sys.executable} -m pip install --upgrade {' '.join(missing_packages)}"
        if not run_command(install_cmd, "Installing missing packages"):
            return False
    
    return True


def build_package():
    """Build the package."""
    return run_command(f"{sys.executable} -m build", "Building package")


def check_package():
    """Check the built package."""
    return run_command(f"{sys.executable} -m twine check dist/*", "Checking package")


def upload_to_test_pypi():
    """Upload to Test PyPI."""
    print("\n🧪 Uploading to Test PyPI...")
    print("You'll need your Test PyPI credentials (https://test.pypi.org)")
    
    cmd = f"{sys.executable} -m twine upload --repository testpypi dist/*"
    return run_command(cmd, "Uploading to Test PyPI")


def upload_to_pypi():
    """Upload to production PyPI."""
    print("\n🚀 Uploading to Production PyPI...")
    print("You'll need your PyPI credentials (https://pypi.org)")
    
    cmd = f"{sys.executable} -m twine upload dist/*"
    return run_command(cmd, "Uploading to Production PyPI")


def test_installation():
    """Test package installation."""
    print("\n🧪 Testing package installation...")
    
    # Test from Test PyPI
    test_cmd = f"{sys.executable} -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ tnsa-api --force-reinstall"
    if run_command(test_cmd, "Testing installation from Test PyPI"):
        # Test import
        test_import_cmd = f'{sys.executable} -c "from tnsa_api_v2 import TNSA; print(\\"✅ Package imported successfully!\\")"'
        run_command(test_import_cmd, "Testing package import")


def main():
    """Main upload process."""
    print("🚀 TNSA API PyPI Upload Tool")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("setup.py").exists():
        print("❌ Error: setup.py not found. Make sure you're in the package directory.")
        return
    
    # Step 1: Check requirements
    if not check_requirements():
        print("❌ Failed to install required tools. Please install manually:")
        print("   pip install --upgrade build twine")
        return
    
    # Step 2: Clean previous builds
    clean_build()
    
    # Step 3: Build package
    if not build_package():
        print("❌ Package build failed. Please check for errors.")
        return
    
    # Step 4: Check package
    if not check_package():
        print("❌ Package check failed. Please fix issues before uploading.")
        return
    
    # Step 5: Ask user what to do
    print("\n📋 Upload Options:")
    print("1. Upload to Test PyPI only (recommended for first time)")
    print("2. Upload to Test PyPI and Production PyPI")
    print("3. Upload to Production PyPI only")
    print("4. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            if upload_to_test_pypi():
                test_installation()
            break
        elif choice == "2":
            if upload_to_test_pypi():
                test_installation()
                input("\nPress Enter to continue to Production PyPI...")
                upload_to_pypi()
            break
        elif choice == "3":
            upload_to_pypi()
            break
        elif choice == "4":
            print("👋 Goodbye!")
            return
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
    
    print("\n🎉 Upload process completed!")
    print("\nNext steps:")
    print("1. Check your package at: https://pypi.org/project/tnsa-api/")
    print("2. Test installation: pip install tnsa-api")
    print("3. Update documentation and GitHub repository")


if __name__ == "__main__":
    main()
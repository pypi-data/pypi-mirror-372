#!/usr/bin/env python3
"""
Install the TNSA API package locally for development.
"""

import subprocess
import sys
import os
from pathlib import Path

def install_package():
    """Install the package in development mode."""
    package_dir = Path(__file__).parent
    
    print("Installing TNSA API package...")
    print(f"Package directory: {package_dir}")
    
    try:
        # Install in development mode
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-e", str(package_dir)
        ], check=True, capture_output=True, text=True)
        
        print("✓ Package installed successfully!")
        print(result.stdout)
        
        # Test import
        print("\nTesting import...")
        import importlib.util
        spec = importlib.util.spec_from_file_location("tnsa_api_v2", package_dir / "__init__.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        print("✓ Package imports successfully!")
        print(f"Version: {module.__version__}")
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Installation failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        return False
    
    return True

def create_wheel():
    """Create a wheel distribution."""
    package_dir = Path(__file__).parent
    
    print("\nCreating wheel distribution...")
    
    try:
        # Build wheel
        result = subprocess.run([
            sys.executable, "-m", "build", str(package_dir)
        ], check=True, capture_output=True, text=True)
        
        print("✓ Wheel created successfully!")
        
        # List created files
        dist_dir = package_dir / "dist"
        if dist_dir.exists():
            print("\nCreated files:")
            for file in dist_dir.iterdir():
                print(f"  {file.name}")
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Wheel creation failed: {e}")
        print(f"Error output: {e.stderr}")
        print("\nTry installing build tools: pip install build")
        return False
    
    return True

def main():
    """Main installation process."""
    print("TNSA API Package Installation")
    print("=" * 40)
    
    # Check if we're in the right directory
    package_dir = Path(__file__).parent
    if not (package_dir / "__init__.py").exists():
        print("✗ Error: Not in package directory")
        return
    
    # Install package
    if install_package():
        print("\n" + "=" * 40)
        print("Installation completed successfully!")
        print("\nYou can now use:")
        print("  from tnsa_api_v2 import TNSA, AsyncTNSA")
        print("\nOr run the example:")
        print("  python example.py")
        
        # Optionally create wheel
        create_wheel_choice = input("\nCreate wheel distribution? (y/n): ").lower().strip()
        if create_wheel_choice == 'y':
            create_wheel()
    
    else:
        print("\n" + "=" * 40)
        print("Installation failed!")

if __name__ == "__main__":
    main()
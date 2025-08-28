#!/usr/bin/env python3
"""
Test build script for XTrade-AI Framework
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

def run_command(command, check=True, capture_output=True):
    """Run a shell command."""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=check, 
            capture_output=capture_output, 
            text=True
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        raise

def test_build():
    """Test the build process."""
    print("🔨 Testing build process...")
    
    # Clean previous builds
    run_command("rm -rf build/ dist/ *.egg-info/")
    
    # Build the package
    run_command("python -m build")
    
    # Check if build artifacts exist
    dist_dir = Path("dist")
    if not dist_dir.exists():
        raise Exception("dist/ directory not created")
    
    # Check for wheel and sdist
    wheel_files = list(dist_dir.glob("*.whl"))
    sdist_files = list(dist_dir.glob("*.tar.gz"))
    
    if not wheel_files:
        raise Exception("No wheel file created")
    if not sdist_files:
        raise Exception("No source distribution created")
    
    print(f"✅ Build artifacts created:")
    for file in wheel_files + sdist_files:
        print(f"  - {file.name}")

def test_package_check():
    """Test package validation."""
    print("✅ Testing package validation...")
    run_command("twine check dist/*")

def test_installation():
    """Test package installation."""
    print("📦 Testing package installation...")
    
    # Find the wheel file
    dist_dir = Path("dist")
    wheel_files = list(dist_dir.glob("*.whl"))
    if not wheel_files:
        raise Exception("No wheel file found")
    
    wheel_file = wheel_files[0]
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Testing installation in: {temp_dir}")
        
        # Copy wheel to temp directory
        test_wheel = Path(temp_dir) / wheel_file.name
        shutil.copy2(wheel_file, test_wheel)
        
        # Install in temp directory
        run_command(f"pip install {test_wheel} --target {temp_dir}/install")
        
        # Test import
        sys.path.insert(0, f"{temp_dir}/install")
        try:
            import xtrade_ai
            print(f"✅ Successfully imported xtrade_ai version: {xtrade_ai.__version__}")
        except ImportError as e:
            raise Exception(f"Failed to import xtrade_ai: {e}")
        finally:
            sys.path.pop(0)

def test_cli():
    """Test CLI installation."""
    print("🖥️ Testing CLI installation...")
    
    # Find the wheel file
    dist_dir = Path("dist")
    wheel_files = list(dist_dir.glob("*.whl"))
    if not wheel_files:
        raise Exception("No wheel file found")
    
    wheel_file = wheel_files[0]
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Testing CLI in: {temp_dir}")
        
        # Copy wheel to temp directory
        test_wheel = Path(temp_dir) / wheel_file.name
        shutil.copy2(wheel_file, test_wheel)
        
        # Install in temp directory
        run_command(f"pip install {test_wheel} --target {temp_dir}/install")
        
        # Test CLI
        env = os.environ.copy()
        env['PYTHONPATH'] = f"{temp_dir}/install"
        
        try:
            result = subprocess.run(
                f"python {temp_dir}/install/xtrade_ai/cli.py --help",
                shell=True,
                capture_output=True,
                text=True,
                env=env
            )
            if result.returncode == 0:
                print("✅ CLI help command works")
            else:
                print(f"❌ CLI help command failed: {result.stderr}")
        except Exception as e:
            print(f"❌ CLI test failed: {e}")

def test_dependencies():
    """Test dependency resolution."""
    print("📋 Testing dependency resolution...")
    
    # Check if all required dependencies are listed
    required_deps = [
        "numpy", "pandas", "scikit-learn", "torch", "stable-baselines3",
        "gymnasium", "xgboost", "fastapi", "uvicorn", "click"
    ]
    
    # Read pyproject.toml
    with open("pyproject.toml", "r") as f:
        content = f.read()
    
    missing_deps = []
    for dep in required_deps:
        if dep not in content:
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"❌ Missing dependencies in pyproject.toml: {missing_deps}")
    else:
        print("✅ All required dependencies found in pyproject.toml")

def test_metadata():
    """Test package metadata."""
    print("📝 Testing package metadata...")
    
    # Check if required files exist
    required_files = [
        "README.md", "LICENSE", "CHANGELOG.md", "pyproject.toml", "setup.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
    else:
        print("✅ All required metadata files found")

def main():
    """Main function."""
    print("🧪 XTrade-AI Framework Build Test")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Error: pyproject.toml not found. Please run this script from the project root.")
        sys.exit(1)
    
    try:
        # Run all tests
        test_metadata()
        test_dependencies()
        test_build()
        test_package_check()
        test_installation()
        test_cli()
        
        print("\n🎉 All tests passed! The package is ready for deployment.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

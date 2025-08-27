#!/usr/bin/env python3
"""
Test script to verify the build process for XTrade-AI Framework
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

def run_command(cmd, cwd=None, check=True):
    """Run a command and return the result."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Command failed: {cmd}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        raise subprocess.CalledProcessError(result.returncode, cmd)
    return result

def test_imports():
    """Test that the package can be imported."""
    print("Testing imports...")
    try:
        import xtrade_ai
        print(f"✓ Main package imported successfully: {xtrade_ai.__version__}")
        
        from xtrade_ai import XTradeAIFramework, XTradeAIConfig
        print("✓ Core classes imported successfully")
        
        from xtrade_ai.utils import get_logger
        print("✓ Utils imported successfully")
        
        from xtrade_ai.modules import technical_analysis
        print("✓ Modules imported successfully")
        
        return True
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        return False

def test_build():
    """Test the build process."""
    print("Testing build process...")
    try:
        # Clean previous builds
        if os.path.exists("dist"):
            shutil.rmtree("dist")
        if os.path.exists("build"):
            shutil.rmtree("build")
        
        # Install build dependencies
        run_command("pip install build twine")
        
        # Build the package
        run_command("python -m build --wheel --sdist")
        
        # Check if build artifacts exist
        if not os.path.exists("dist"):
            print("✗ Build failed: dist directory not created")
            return False
        
        dist_files = os.listdir("dist")
        print(f"✓ Build artifacts created: {dist_files}")
        
        # Check package
        run_command("twine check dist/*")
        print("✓ Package validation passed")
        
        return True
    except Exception as e:
        print(f"✗ Build test failed: {e}")
        return False

def test_installation():
    """Test installing the built package."""
    print("Testing package installation...")
    try:
        # Find wheel file
        dist_dir = Path("dist")
        wheel_files = list(dist_dir.glob("*.whl"))
        
        if not wheel_files:
            print("✗ No wheel files found")
            return False
        
        wheel_file = wheel_files[0]
        print(f"Installing: {wheel_file}")
        
        # Install in a temporary environment
        with tempfile.TemporaryDirectory() as temp_dir:
            # Install the wheel
            run_command(f"pip install {wheel_file} --target {temp_dir}")
            
            # Test import in the installed location
            sys.path.insert(0, temp_dir)
            try:
                import xtrade_ai
                print("✓ Package installed and importable")
                return True
            except Exception as e:
                print(f"✗ Installation test failed: {e}")
                return False
            finally:
                sys.path.pop(0)
                
    except Exception as e:
        print(f"✗ Installation test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("XTrade-AI Framework Build Test")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Build Test", test_build),
        ("Installation Test", test_installation),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    all_passed = True
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{test_name}: {status}")
        if not success:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests passed! Build is ready for deployment.")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Test script to simulate ReadTheDocs build environment.
This helps debug documentation build issues locally.
"""

import os
import sys
import subprocess
import tempfile
import shutil

def test_rtd_build():
    """Test the ReadTheDocs build process locally."""
    
    # Set up environment variables like ReadTheDocs
    os.environ['READTHEDOCS'] = 'True'
    os.environ['READTHEDOCS_VERSION'] = 'latest'
    os.environ['READTHEDOCS_PROJECT'] = 'xtrade-ai'
    
    print("Testing ReadTheDocs build environment...")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    
    # Test if we can import the required modules
    try:
        import sphinx
        print(f"✓ Sphinx version: {sphinx.__version__}")
    except ImportError as e:
        print(f"✗ Failed to import sphinx: {e}")
        return False
    
    try:
        import myst_parser
        print(f"✓ MyST Parser version: {myst_parser.__version__}")
    except ImportError as e:
        print(f"✗ Failed to import myst_parser: {e}")
        return False
    
    # Test if we can import the main package
    try:
        import xtrade_ai
        print(f"✓ XTrade-AI package imported successfully")
    except ImportError as e:
        print(f"⚠ XTrade-AI package not available: {e}")
        print("This is expected in some environments")
    
    # Test Sphinx configuration
    try:
        sys.path.insert(0, os.path.abspath('.'))
        from docs.conf import extensions, project, author
        print(f"✓ Sphinx config loaded successfully")
        print(f"  Project: {project}")
        print(f"  Author: {author}")
        print(f"  Extensions: {len(extensions)} extensions loaded")
    except Exception as e:
        print(f"✗ Failed to load Sphinx config: {e}")
        return False
    
    # Test documentation build
    print("\nTesting documentation build...")
    try:
        result = subprocess.run([
            sys.executable, '-m', 'sphinx', 
            '-b', 'html', 
            '-d', '_build/doctrees',
            '-D', 'language=en',
            'docs', '_build/html'
        ], capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            print("✓ Documentation build successful!")
            return True
        else:
            print(f"✗ Documentation build failed:")
            print(f"Return code: {result.returncode}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Failed to run sphinx-build: {e}")
        return False

if __name__ == "__main__":
    success = test_rtd_build()
    sys.exit(0 if success else 1)

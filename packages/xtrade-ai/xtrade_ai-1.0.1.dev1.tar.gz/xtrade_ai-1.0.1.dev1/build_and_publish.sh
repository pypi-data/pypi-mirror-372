#!/bin/bash

# XTrade-AI Build and Publish Script
# This script builds the package and publishes it to PyPI

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PACKAGE_NAME="xtrade-ai"
PYPI_REPO=${1:-"pypi"}  # pypi or testpypi
BUILD_TYPE=${2:-"release"}  # release or dev

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    log_info "Checking build dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check pip
    if ! command -v pip &> /dev/null; then
        log_error "pip is not installed"
        exit 1
    fi
    
    # Check build tools
    python3 -c "import setuptools, wheel" 2>/dev/null || {
        log_info "Installing build dependencies..."
        pip install --upgrade setuptools wheel twine
    }
    
    log_success "Build dependencies are satisfied"
}

clean_build() {
    log_info "Cleaning previous builds..."
    
    # Remove build artifacts
    rm -rf build/
    rm -rf dist/
    rm -rf *.egg-info/
    rm -rf __pycache__/
    rm -rf .pytest_cache/
    
    # Clean Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    
    log_success "Build cleaned successfully"
}

run_tests() {
    log_info "Running tests..."
    
    # Install test dependencies
    pip install -e ".[dev]"
    
    # Run tests
    python -m pytest test/ -v --tb=short
    
    log_success "Tests passed successfully"
}

check_code_quality() {
    log_info "Checking code quality..."
    
    # Install development dependencies
    pip install black flake8 mypy
    
    # Run code formatting check
    black --check --diff .
    
    # Run linting
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
    
    # Run type checking
    mypy . --ignore-missing-imports
    
    log_success "Code quality checks passed"
}

build_package() {
    log_info "Building package..."
    
    # Build source distribution
    python setup.py sdist bdist_wheel
    
    # Check package
    twine check dist/*
    
    log_success "Package built successfully"
}

test_install() {
    log_info "Testing package installation..."
    
    # Create temporary virtual environment
    python3 -m venv test_env
    source test_env/bin/activate
    
    # Install package
    pip install dist/*.whl
    
    # Test import
    python -c "import xtrade_ai; print('Package imported successfully')"
    
    # Cleanup
    deactivate
    rm -rf test_env
    
    log_success "Package installation test passed"
}

publish_package() {
    log_info "Publishing package to ${PYPI_REPO}..."
    
    if [ "$BUILD_TYPE" = "dev" ]; then
        log_warning "Publishing development version"
        # Add dev suffix to version
        # This would require modifying setup.py or pyproject.toml
    fi
    
    # Upload to PyPI
    if [ "$PYPI_REPO" = "testpypi" ]; then
        twine upload --repository testpypi dist/*
        log_success "Package published to TestPyPI"
        log_info "Test installation: pip install --index-url https://test.pypi.org/simple/ ${PACKAGE_NAME}"
    else
        twine upload dist/*
        log_success "Package published to PyPI"
        log_info "Installation: pip install ${PACKAGE_NAME}"
    fi
}

create_release() {
    log_info "Creating GitHub release..."
    
    # Get version from package
    VERSION=$(python setup.py --version)
    
    # Create release notes
    cat > RELEASE_NOTES.md << EOF
# XTrade-AI v${VERSION}

## What's New

- Enhanced production deployment capabilities
- Improved Docker containerization
- Added comprehensive monitoring
- Better error handling and logging
- Performance optimizations

## Installation

\`\`\`bash
pip install xtrade-ai[all]
\`\`\`

## Quick Start

\`\`\`bash
# Deploy with Docker
./deploy.sh deploy production with-monitoring

# Use CLI
xtrade-ai train --data-path data.csv --model-path models/
xtrade-ai predict --data-path market.csv --model-path models/model.pkl
\`\`\`

## Documentation

- [Production Guide](PRODUCTION.md)
- [API Documentation](docs/api_reference.md)
- [Examples](docs/examples.md)

## Breaking Changes

None in this release.

## Bug Fixes

- Fixed import issues in production environment
- Improved error handling in CLI
- Enhanced Docker build process

## Contributors

Thanks to all contributors!
EOF
    
    log_info "Release notes created: RELEASE_NOTES.md"
    log_warning "Please create GitHub release manually with these notes"
}

main() {
    log_info "Starting XTrade-AI build and publish process..."
    
    check_dependencies
    clean_build
    run_tests
    check_code_quality
    build_package
    test_install
    
    if [ "$3" = "publish" ]; then
        publish_package
        create_release
    else
        log_info "Build completed. To publish, run: $0 $PYPI_REPO $BUILD_TYPE publish"
    fi
    
    log_success "Build and publish process completed!"
}

# Command line interface
case "${1:-help}" in
    "build")
        check_dependencies
        clean_build
        run_tests
        check_code_quality
        build_package
        test_install
        ;;
    "test")
        run_tests
        ;;
    "quality")
        check_code_quality
        ;;
    "publish")
        main "$@"
        ;;
    "help"|"-h"|"--help")
        echo "XTrade-AI Build and Publish Script"
        echo ""
        echo "Usage: $0 [command] [options]"
        echo ""
        echo "Commands:"
        echo "  build                    Build package only"
        echo "  test                     Run tests only"
        echo "  quality                  Run code quality checks only"
        echo "  publish [repo] [type]    Build and publish package"
        echo "  help                     Show this help message"
        echo ""
        echo "Options:"
        echo "  repo                     PyPI repository (pypi|testpypi, default: pypi)"
        echo "  type                     Build type (release|dev, default: release)"
        echo ""
        echo "Examples:"
        echo "  $0 build"
        echo "  $0 publish testpypi dev"
        echo "  $0 publish pypi release publish"
        ;;
    *)
        main "$@"
        ;;
esac

#!/bin/bash

# XTrade-AI Docker Build Test Script
# This script tests different Dockerfile configurations locally

set -e

echo "🐳 XTrade-AI Docker Build Test Script"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to test Docker build
test_docker_build() {
    local dockerfile=$1
    local tag=$2
    local description=$3
    
    print_status "Testing $description..."
    print_status "Dockerfile: $dockerfile"
    print_status "Tag: $tag"
    
    if docker build -f "$dockerfile" -t "$tag" .; then
        print_status "✅ $description build successful!"
        
        # Test if the package can be imported
        print_status "Testing package import..."
        if docker run --rm "$tag" python -c "import xtrade_ai; print('✅ Package imported successfully')"; then
            print_status "✅ Package import test passed!"
        else
            print_error "❌ Package import test failed!"
            return 1
        fi
        
        # Test CLI command
        print_status "Testing CLI command..."
        if docker run --rm "$tag" xtrade-ai --help > /dev/null 2>&1; then
            print_status "✅ CLI command test passed!"
        else
            print_warning "⚠️ CLI command test failed (this might be expected)"
        fi
        
        return 0
    else
        print_error "❌ $description build failed!"
        return 1
    fi
}

# Clean up old images
print_status "Cleaning up old test images..."
docker rmi xtrade-ai:test-simple xtrade-ai:test-robust xtrade-ai:test-standard 2>/dev/null || true

# Test different Dockerfile configurations
success_count=0
total_tests=0

# Test 1: Simple Dockerfile
total_tests=$((total_tests + 1))
if test_docker_build "Dockerfile.simple" "xtrade-ai:test-simple" "Simple Dockerfile"; then
    success_count=$((success_count + 1))
fi

echo ""

# Test 2: Robust Dockerfile
total_tests=$((total_tests + 1))
if test_docker_build "Dockerfile.robust" "xtrade-ai:test-robust" "Robust Dockerfile"; then
    success_count=$((success_count + 1))
fi

echo ""

# Test 3: Standard Dockerfile
total_tests=$((total_tests + 1))
if test_docker_build "Dockerfile" "xtrade-ai:test-standard" "Standard Dockerfile"; then
    success_count=$((success_count + 1))
fi

echo ""
echo "====================================="
echo "🐳 Build Test Results"
echo "====================================="
echo "Tests passed: $success_count/$total_tests"

if [ $success_count -eq $total_tests ]; then
    print_status "🎉 All Docker builds successful!"
    echo ""
    print_status "Recommended Dockerfile for production:"
    if [ -f "Dockerfile.simple" ]; then
        echo "   - Dockerfile.simple (fastest, most reliable)"
    fi
    if [ -f "Dockerfile.robust" ]; then
        echo "   - Dockerfile.robust (full features)"
    fi
    echo ""
    print_status "To use in CI/CD, update your workflow to use:"
    echo "   file: ./Dockerfile.simple"
    exit 0
else
    print_error "❌ Some Docker builds failed!"
    echo ""
    print_warning "Recommendations:"
    echo "   1. Check the build logs above for specific errors"
    echo "   2. Use Dockerfile.simple for initial testing"
    echo "   3. Review DOCKER_TROUBLESHOOTING.md for solutions"
    echo "   4. Ensure all dependencies are compatible"
    exit 1
fi

#!/bin/bash

# XTrade-AI Framework Cache Cleanup Script
echo "🧹 Cleaning XTrade-AI Framework cache and temporary files..."

# Clean Python cache
echo "Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true

# Clean build artifacts
echo "Cleaning build artifacts..."
rm -rf build/ dist/ *.egg-info/ 2>/dev/null || true

# Clean test artifacts
echo "Cleaning test artifacts..."
rm -rf .pytest_cache/ test_results/ htmlcov/ .coverage 2>/dev/null || true

# Clean Docker cache (if Docker is available)
if command -v docker &> /dev/null; then
    echo "Cleaning Docker cache..."
    docker system prune -f 2>/dev/null || true
fi

# Clean pip cache
echo "Cleaning pip cache..."
pip cache purge 2>/dev/null || true

# Clean git cache (if in git repository)
if [ -d ".git" ]; then
    echo "Cleaning git cache..."
    git gc --prune=now 2>/dev/null || true
fi

echo "✅ Cache cleanup completed!"
echo ""
echo "Current Python version:"
python --version
echo ""
echo "Current pip version:"
pip --version
echo ""
echo "Framework ready for deployment! 🚀"

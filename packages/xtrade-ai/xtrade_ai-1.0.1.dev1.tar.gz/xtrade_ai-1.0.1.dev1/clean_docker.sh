#!/bin/bash

# XTrade-AI Docker Cleanup Script
echo "🧹 Cleaning Docker build cache and artifacts..."

# Remove all unused containers, networks, images (both dangling and unreferenced)
echo "📦 Removing unused Docker containers, networks, and images..."
docker system prune -a -f

# Remove all build cache
echo "🗑️  Removing Docker build cache..."
docker builder prune -a -f

# Remove dangling images
echo "🖼️  Removing dangling images..."
docker image prune -f

# Remove unused volumes
echo "💾 Removing unused volumes..."
docker volume prune -f

# Clean up any remaining artifacts
echo "🧽 Cleaning up remaining artifacts..."
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/
rm -rf __pycache__/
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

echo "✅ Docker cleanup completed!"
echo "💡 To see space saved, run: docker system df"

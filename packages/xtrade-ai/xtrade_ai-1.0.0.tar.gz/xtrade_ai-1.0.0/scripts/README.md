# Scripts Directory

This directory contains all build, deployment, and utility scripts for the XTrade-AI framework.

## Directory Structure

```
scripts/
├── build/           # Build and packaging scripts
├── deploy/          # Deployment scripts
├── clean/           # Cleanup scripts
├── Makefile         # Main Makefile for common tasks
└── README.md        # This file
```

## Build Scripts (`build/`)

- `build_and_publish.sh` - Build package and publish to PyPI
- `test_docker_build.sh` - Test Docker image builds
- `test_build.py` - Python build testing script

## Deploy Scripts (`deploy/`)

- `deploy.sh` - Linux/macOS deployment script
- `deploy.ps1` - Windows PowerShell deployment script

## Clean Scripts (`clean/`)

- `clean_cache.sh` - Clean build cache and artifacts
- `clean_cache.ps1` - Windows cache cleanup
- `clean_docker.sh` - Clean Docker containers and images

## Usage

### Using Makefile (Recommended)

```bash
# Navigate to scripts directory
cd scripts

# Install dependencies
make install

# Build package
make build

# Run tests
make test

# Deploy
make deploy

# Clean
make clean
```

### Direct Script Usage

```bash
# Build and publish
./build/build_and_publish.sh

# Deploy
./deploy/deploy.sh

# Clean cache
./clean/clean_cache.sh
```

## Requirements

- Python 3.8+
- Docker (for containerized builds)
- Make (for Makefile usage)
- Bash (for shell scripts)
- PowerShell (for Windows scripts)

## Configuration

The scripts use the following directory structure:
- `../requirements/` - Python dependencies
- `../config/` - Configuration files
- `../docker/` - Docker files
- `../xtrade_ai/` - Main package source

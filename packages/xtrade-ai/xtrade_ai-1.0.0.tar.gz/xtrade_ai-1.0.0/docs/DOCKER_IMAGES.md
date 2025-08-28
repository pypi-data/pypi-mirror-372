# XTrade-AI Docker Images

This document provides an overview of all available Docker images for the XTrade-AI framework, including their categories, descriptions, use cases, and deployment scenarios.

## Image Categories

### 1. **Production-Ready PyPI Distribution** (`Dockerfile.pypi`)
- **Category**: Production-Ready PyPI Distribution
- **Description**: Optimized Docker image for XTrade-AI framework installed from PyPI
- **Use case**: Production deployments with PyPI package management
- **Size**: Medium (optimized for production)
- **Base**: `python:3.11-slim`
- **Features**:
  - Installs from PyPI package
  - Multi-stage build for optimization
  - Minimal runtime dependencies
  - Production-ready configuration
- **Best for**: Production deployments where you want to use the published PyPI package

### 2. **Full Production Build** (`Dockerfile`)
- **Category**: Full Production Build
- **Description**: Complete XTrade-AI framework with all dependencies and source code
- **Use case**: Production deployments with full feature set and development tools
- **Size**: Large (includes all dependencies and source)
- **Base**: `python:3.11-slim`
- **Features**:
  - Complete source code included
  - All development tools
  - Full dependency set
  - Multiple fallback installation strategies
- **Best for**: Production deployments requiring full source access and development capabilities

### 3. **Minimal Production Build** (`Dockerfile.minimal`)
- **Category**: Minimal Production Build
- **Description**: Lightweight XTrade-AI framework with minimal dependencies
- **Use case**: Production deployments with minimal resource usage
- **Size**: Small (optimized for minimal footprint)
- **Base**: `python:3.11-alpine`
- **Features**:
  - Alpine Linux base for smaller size
  - Minimal dependencies
  - Essential features only
  - Resource-optimized
- **Best for**: Resource-constrained environments, containers, and edge deployments

### 4. **Optimized Production Build** (`Dockerfile.simple`)
- **Category**: Optimized Production Build
- **Description**: Balanced XTrade-AI framework with optimized dependencies and build process
- **Use case**: Production deployments with good balance of features and performance
- **Size**: Medium (optimized for production)
- **Base**: `python:3.11-slim`
- **Features**:
  - Multi-stage build optimization
  - Balanced feature set
  - Production-ready configuration
  - Good performance characteristics
- **Best for**: General production deployments with balanced requirements

### 5. **Robust Production Build** (`Dockerfile.robust`)
- **Category**: Robust Production Build
- **Description**: XTrade-AI framework with enhanced error handling and fallback strategies
- **Use case**: Production deployments requiring maximum reliability and error recovery
- **Size**: Large (includes all dependencies and robust error handling)
- **Base**: `python:3.11-slim`
- **Features**:
  - Enhanced error handling
  - Multiple fallback installation strategies
  - Maximum reliability
  - Comprehensive error recovery
- **Best for**: High-reliability production environments

## Image Comparison

| Image Type | Size | Base | Use Case | Features | Reliability |
|------------|------|------|----------|----------|-------------|
| PyPI | Medium | python:3.11-slim | Production PyPI | PyPI package, optimized | High |
| Full | Large | python:3.11-slim | Full Production | Complete source, dev tools | High |
| Minimal | Small | python:3.11-alpine | Resource-constrained | Essential features | Medium |
| Optimized | Medium | python:3.11-slim | General Production | Balanced features | High |
| Robust | Large | python:3.11-slim | High-reliability | Error handling, fallbacks | Very High |

## Usage Examples

### PyPI-based Deployment
```bash
# Build PyPI image
docker build -f Dockerfile.pypi -t xtrade-ai:pypi .

# Run PyPI image
docker run -it xtrade-ai:pypi xtrade-ai --help
```

### Minimal Deployment
```bash
# Build minimal image
docker build -f Dockerfile.minimal -t xtrade-ai:minimal .

# Run minimal image
docker run -it xtrade-ai:minimal xtrade-ai --help
```

### Full Production Deployment
```bash
# Build full image
docker build -f Dockerfile -t xtrade-ai:full .

# Run full image
docker run -it xtrade-ai:full xtrade-ai --help
```

### Optimized Deployment
```bash
# Build optimized image
docker build -f Dockerfile.simple -t xtrade-ai:optimized .

# Run optimized image
docker run -it xtrade-ai:optimized xtrade-ai --help
```

### Robust Deployment
```bash
# Build robust image
docker build -f Dockerfile.robust -t xtrade-ai:robust .

# Run robust image
docker run -it xtrade-ai:robust xtrade-ai --help
```

## Docker Compose Integration

All images can be used with Docker Compose. Example configuration:

```yaml
version: '3.8'
services:
  xtrade-ai-pypi:
    build:
      context: .
      dockerfile: Dockerfile.pypi
    image: xtrade-ai:pypi
    container_name: xtrade-ai-pypi
    volumes:
      - ./data:/app/data
      - ./models:/app/models
      - ./logs:/app/logs
      - ./config:/app/config
    environment:
      - XTRADE_DATA_DIR=/app/data
      - XTRADE_MODEL_DIR=/app/models
      - XTRADE_LOG_DIR=/app/logs
      - XTRADE_CONFIG_DIR=/app/config

  xtrade-ai-minimal:
    build:
      context: .
      dockerfile: Dockerfile.minimal
    image: xtrade-ai:minimal
    container_name: xtrade-ai-minimal
    volumes:
      - ./data:/app/data
      - ./models:/app/models
      - ./logs:/app/logs
      - ./config:/app/config
```

## Image Metadata

All images include comprehensive metadata labels:

- **Maintainer**: XTrade-AI Team
- **Title**: Descriptive image title
- **Description**: Detailed image description
- **Vendor**: XTrade-AI
- **Source**: GitHub repository
- **License**: MIT
- **Category**: ai-trading
- **Type**: application
- **Version**: 1.0.0
- **Custom Labels**: xtrade.category, xtrade.type, xtrade.optimization, xtrade.use-case, xtrade.features

## Best Practices

1. **Choose the right image** based on your deployment requirements
2. **Use PyPI image** for production deployments with package management
3. **Use minimal image** for resource-constrained environments
4. **Use robust image** for high-reliability requirements
5. **Use optimized image** for general production use
6. **Use full image** when you need development capabilities

## Troubleshooting

For troubleshooting information, see [DOCKER_TROUBLESHOOTING.md](DOCKER_TROUBLESHOOTING.md).

## Support

For support and questions about Docker images, please refer to the main documentation or create an issue in the GitHub repository.

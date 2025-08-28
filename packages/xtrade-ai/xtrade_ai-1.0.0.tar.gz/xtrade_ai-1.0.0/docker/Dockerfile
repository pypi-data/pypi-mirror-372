# XTrade-AI Framework Production Dockerfile
# Category: Full Production Build
# Description: Complete XTrade-AI framework installed from PyPI
# Use case: Production deployments with full feature set
# Size: Medium (PyPI package + dependencies)
# Base: python:3.11-slim

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Add metadata labels
LABEL maintainer="XTrade-AI Team <anasamu7@gmail.com>"
LABEL org.opencontainers.image.title="XTrade-AI Framework"
LABEL org.opencontainers.image.description="XTrade-AI framework installed from PyPI with all dependencies"
LABEL org.opencontainers.image.vendor="XTrade-AI"
LABEL org.opencontainers.image.source="https://github.com/anasamu7/xtrade-ai-framework"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.category="ai-trading"
LABEL org.opencontainers.image.type="application"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.created="2024-01-01T00:00:00Z"
LABEL xtrade.category="production"
LABEL xtrade.type="pypi"
LABEL xtrade.optimization="medium"
LABEL xtrade.use-case="production-deployment"
LABEL xtrade.features="complete"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    wget \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install build tools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install XTrade-AI framework from PyPI with all optional dependencies
RUN pip install --no-cache-dir \
    xtrade-ai[all] \
    && pip cache purge

# Create necessary directories
RUN mkdir -p /app/data /app/models /app/logs /app/config

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash xtrade && \
    chown -R xtrade:xtrade /app
USER xtrade

# Set default environment
ENV XTRADE_DATA_DIR=/app/data
ENV XTRADE_MODEL_DIR=/app/models
ENV XTRADE_LOG_DIR=/app/logs
ENV XTRADE_CONFIG_DIR=/app/config

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import xtrade_ai; print('XTrade-AI Framework is healthy')" || exit 1

# Expose API port
EXPOSE 8000

# Default command - start API server
CMD ["xtrade-ai", "start-api", "--host", "0.0.0.0", "--port", "8000"]

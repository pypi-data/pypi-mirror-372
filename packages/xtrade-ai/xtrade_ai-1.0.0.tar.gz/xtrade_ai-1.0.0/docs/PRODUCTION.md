# XTrade-AI Production Deployment Guide

This guide provides comprehensive instructions for deploying the XTrade-AI framework in a production environment using Docker and Docker Compose.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Deployment](#deployment)
6. [Monitoring](#monitoring)
7. [Scaling](#scaling)
8. [Security](#security)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+ recommended), macOS, or Windows with WSL2
- **Docker**: Version 20.10+ with Docker Compose
- **Memory**: Minimum 8GB RAM (16GB+ recommended)
- **Storage**: Minimum 50GB free space
- **CPU**: 4+ cores recommended

### Software Dependencies

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/xtrade-ai.git
cd xtrade-ai
```

### 2. Deploy with Monitoring

```bash
# Make deployment script executable
chmod +x deploy.sh

# Deploy with monitoring
./deploy.sh deploy production with-monitoring
```

### 3. Access the Application

- **Main Application**: http://localhost
- **API Documentation**: http://localhost/docs
- **Grafana Dashboard**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

## Installation

### Option 1: Using pip (Recommended)

```bash
# Install from PyPI
pip install xtrade-ai

# Or install with specific features
pip install xtrade-ai[ta,monitor,performance]
```

### Option 2: From Source

```bash
# Clone and install
git clone https://github.com/your-org/xtrade-ai.git
cd xtrade-ai
pip install -e .
```

### Option 3: Docker Installation

```bash
# Build and run with Docker
docker build -t xtrade-ai .
docker run -p 8000:8000 xtrade-ai
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# XTrade-AI Environment Configuration
XTRADE_ENV=production
XTRADE_LOG_LEVEL=INFO
XTRADE_DATA_DIR=/app/data
XTRADE_MODEL_DIR=/app/models
XTRADE_LOG_DIR=/app/logs
XTRADE_CONFIG_DIR=/app/config

# Database Configuration
POSTGRES_DB=xtrade_ai
POSTGRES_USER=xtrade_user
POSTGRES_PASSWORD=your-secure-password

# Redis Configuration
REDIS_URL=redis://redis:6379

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true
```

### Configuration Files

#### Trading Configuration (`config/trading.yaml`)

```yaml
trading:
  initial_balance: 10000.0
  max_positions: 10
  risk_tolerance: 0.02
  stop_loss: 0.02
  take_profit: 0.05
  commission_rate: 0.001
  slippage: 0.0005

model:
  state_dim: 545
  action_dim: 4
  hidden_dim: 128
  learning_rate: 3e-4
  batch_size: 64
  enable_xgboost: true
  enable_risk_management: true
```

## Deployment

### Using the Deployment Script

```bash
# Full deployment with monitoring
./deploy.sh deploy production with-monitoring

# Basic deployment
./deploy.sh deploy production

# Start services
./deploy.sh start

# Check status
./deploy.sh status

# View logs
./deploy.sh logs

# Stop services
./deploy.sh stop
```

### Manual Docker Compose Deployment

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Start with monitoring
docker-compose --profile monitoring up -d

# Scale services
docker-compose up -d --scale xtrade-ai=3
```

### Production Deployment Checklist

- [ ] Set secure passwords in `.env`
- [ ] Configure SSL certificates
- [ ] Set up backup strategy
- [ ] Configure monitoring alerts
- [ ] Set up log rotation
- [ ] Configure firewall rules
- [ ] Set up automated backups
- [ ] Test disaster recovery

## Monitoring

### Built-in Monitoring

The framework includes comprehensive monitoring capabilities:

#### Prometheus Metrics

- **Application Metrics**: Request rates, response times, error rates
- **Trading Metrics**: P&L, win rate, Sharpe ratio, drawdown
- **System Metrics**: CPU, memory, disk usage
- **Model Metrics**: Training progress, prediction accuracy

#### Grafana Dashboards

Pre-configured dashboards for:
- Trading Performance
- System Health
- Model Performance
- Risk Metrics

### Custom Monitoring

```python
from xtrade_ai import XTradeAIFramework
from xtrade_ai.modules.monitoring import MonitoringModule

# Initialize monitoring
monitor = MonitoringModule()

# Track custom metrics
monitor.track_metric("custom_metric", value=42)
monitor.track_event("important_event", {"detail": "value"})
```

## Scaling

### Horizontal Scaling

```bash
# Scale the main application
docker-compose up -d --scale xtrade-ai=3

# Scale with load balancer
docker-compose -f docker-compose.yml -f docker-compose.scale.yml up -d
```

### Vertical Scaling

```yaml
# docker-compose.override.yml
services:
  xtrade-ai:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G
```

### Database Scaling

```bash
# Use read replicas
docker-compose -f docker-compose.yml -f docker-compose.db.yml up -d

# Use connection pooling
docker-compose -f docker-compose.yml -f docker-compose.pool.yml up -d
```

## Security

### Security Best Practices

1. **Use HTTPS**: Configure SSL certificates
2. **Secure Passwords**: Use strong, unique passwords
3. **Network Security**: Configure firewalls and VPNs
4. **Access Control**: Implement proper authentication
5. **Data Encryption**: Encrypt sensitive data
6. **Regular Updates**: Keep dependencies updated

### Security Configuration

```yaml
# nginx.conf security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Strict-Transport-Security "max-age=63072000" always;
```

### SSL Configuration

```bash
# Generate SSL certificates
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/private.key -out ssl/certificate.crt

# Update nginx configuration
# Uncomment HTTPS server block in nginx.conf
```

## Troubleshooting

### Common Issues

#### Service Won't Start

```bash
# Check logs
docker-compose logs xtrade-ai

# Check health
docker-compose ps

# Restart services
docker-compose restart
```

#### Database Connection Issues

```bash
# Check database status
docker-compose exec postgres pg_isready -U xtrade_user

# Check database logs
docker-compose logs postgres
```

#### Memory Issues

```bash
# Check memory usage
docker stats

# Increase memory limits
docker-compose down
docker-compose up -d --scale xtrade-ai=1
```

### Performance Optimization

#### Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_trades_timestamp ON trades(timestamp);
CREATE INDEX idx_positions_symbol ON positions(symbol);

-- Optimize queries
ANALYZE trades;
ANALYZE positions;
```

#### Application Optimization

```python
# Enable caching
from xtrade_ai.utils.memory_manager import get_memory_manager
memory_manager = get_memory_manager()
memory_manager.enable_caching()

# Optimize model loading
framework.load_model("/path/to/model", lazy=True)
```

### Log Analysis

```bash
# View application logs
docker-compose logs -f xtrade-ai

# Search for errors
docker-compose logs xtrade-ai | grep ERROR

# Monitor real-time logs
docker-compose logs -f --tail=100 xtrade-ai
```

## Support

For additional support:

- **Documentation**: https://xtrade-ai.readthedocs.io
- **Issues**: https://github.com/your-org/xtrade-ai/issues
- **Discussions**: https://github.com/your-org/xtrade-ai/discussions
- **Email**: support@xtrade-ai.com

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

# Deployment Guide

This guide covers all deployment methods for the XTrade-AI framework, including local installation, Docker deployment, cloud deployment, and production considerations.

## Table of Contents

- [Installation Methods](#installation-methods)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Production Deployment](#production-deployment)
- [Configuration Management](#configuration-management)
- [Monitoring and Logging](#monitoring-and-logging)
- [Security Considerations](#security-considerations)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting](#troubleshooting)

## Installation Methods

### PyPI Installation (Recommended)

The easiest way to install XTrade-AI is through PyPI:

```bash
# Install the latest stable version
pip install xtrade-ai

# Install with optional dependencies
pip install xtrade-ai[full]

# Install specific version
pip install xtrade-ai==1.0.1
```

### Docker Installation

Pull the official Docker image:

```bash
# Pull latest version
docker pull anasamu7/xtrade-ai:latest

# Pull specific version
docker pull anasamu7/xtrade-ai:1.0.1

# Run the container
docker run -it --rm anasamu7/xtrade-ai:latest
```

## Docker Deployment

### Using Official Images

The framework provides multiple Docker images optimized for different use cases:

#### Production Image (Recommended)

```bash
# Pull and run production image
docker pull anasamu7/xtrade-ai:latest
docker run -d \
  --name xtrade-ai \
  -p 8000:8000 \
  -v /path/to/data:/app/data \
  -v /path/to/models:/app/models \
  -e ENVIRONMENT=production \
  anasamu7/xtrade-ai:latest
```

#### Minimal Image

For resource-constrained environments:

```bash
docker run -d \
  --name xtrade-ai-minimal \
  --memory=2g \
  --cpus=1 \
  anasamu7/xtrade-ai:minimal
```

### Custom Docker Build

Build your own Docker image:

```dockerfile
# Use the official image as base
FROM anasamu7/xtrade-ai:latest

# Add custom configurations
COPY config.yaml /app/config.yaml
COPY models/ /app/models/

# Set environment variables
ENV ENVIRONMENT=production
ENV LOG_LEVEL=INFO

# Expose ports
EXPOSE 8000

# Run the application
CMD ["python", "-m", "xtrade_ai.cli", "start"]
```

Build and run:

```bash
docker build -t my-xtrade-ai .
docker run -d --name my-xtrade-ai my-xtrade-ai
```

### Docker Compose

For complex deployments with multiple services:

```yaml
# docker-compose.yml
version: '3.8'

services:
  xtrade-ai:
    image: anasamu7/xtrade-ai:latest
    container_name: xtrade-ai
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./models:/app/models
      - ./logs:/app/logs
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
      - DATABASE_URL=postgresql://user:pass@db:5432/xtrade
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:13
    container_name: xtrade-db
    environment:
      - POSTGRES_DB=xtrade
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    container_name: xtrade-redis
    restart: unless-stopped

volumes:
  postgres_data:
```

Run with:

```bash
docker-compose up -d
```

## Cloud Deployment

### AWS Deployment

#### EC2 Instance

1. **Launch EC2 Instance**:
   ```bash
   # Using AWS CLI
   aws ec2 run-instances \
     --image-id ami-0c02fb55956c7d316 \
     --instance-type t3.medium \
     --key-name your-key-pair \
     --security-group-ids sg-xxxxxxxxx \
     --subnet-id subnet-xxxxxxxxx
   ```

2. **Install Dependencies**:
   ```bash
   # Connect to instance
   ssh -i your-key.pem ubuntu@your-instance-ip

   # Update system
   sudo apt update && sudo apt upgrade -y

   # Install Python and dependencies
   sudo apt install python3 python3-pip python3-venv -y

   # Install XTrade-AI
   pip3 install xtrade-ai
   ```

3. **Configure Application**:
   ```bash
   # Create application directory
   mkdir -p /opt/xtrade-ai
   cd /opt/xtrade-ai

   # Create configuration
   cat > config.yaml << EOF
   environment: production
   log_level: INFO
   data_path: /opt/xtrade-ai/data
   models_path: /opt/xtrade-ai/models
   EOF
   ```

4. **Setup Systemd Service**:
   ```bash
   sudo tee /etc/systemd/system/xtrade-ai.service << EOF
   [Unit]
   Description=XTrade-AI Trading Framework
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/opt/xtrade-ai
   ExecStart=/usr/local/bin/python3 -m xtrade_ai.cli start
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   EOF

   # Enable and start service
   sudo systemctl enable xtrade-ai
   sudo systemctl start xtrade-ai
   ```

#### ECS/Fargate

```yaml
# task-definition.json
{
  "family": "xtrade-ai",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "xtrade-ai",
      "image": "anasamu7/xtrade-ai:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/xtrade-ai",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Google Cloud Platform

#### Compute Engine

```bash
# Create instance
gcloud compute instances create xtrade-ai \
  --zone=us-central1-a \
  --machine-type=e2-medium \
  --image-family=debian-11 \
  --image-project=debian-cloud \
  --boot-disk-size=20GB

# Install dependencies
gcloud compute ssh xtrade-ai --zone=us-central1-a
sudo apt update && sudo apt install python3 python3-pip -y
pip3 install xtrade-ai
```

#### Cloud Run

```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/xtrade-ai', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/xtrade-ai']
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'xtrade-ai'
      - '--image'
      - 'gcr.io/$PROJECT_ID/xtrade-ai'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
```

### Azure

#### Azure Container Instances

```bash
# Deploy to ACI
az container create \
  --resource-group myResourceGroup \
  --name xtrade-ai \
  --image anasamu7/xtrade-ai:latest \
  --dns-name-label xtrade-ai \
  --ports 8000 \
  --environment-variables ENVIRONMENT=production
```

#### Azure Kubernetes Service

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: xtrade-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: xtrade-ai
  template:
    metadata:
      labels:
        app: xtrade-ai
    spec:
      containers:
      - name: xtrade-ai
        image: anasamu7/xtrade-ai:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: xtrade-ai-service
spec:
  selector:
    app: xtrade-ai
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Production Deployment

### Environment Configuration

Create environment-specific configurations:

```yaml
# config/production.yaml
environment: production
log_level: INFO
debug: false

# Database configuration
database:
  url: postgresql://user:pass@localhost:5432/xtrade_prod
  pool_size: 20
  max_overflow: 30

# Redis configuration
redis:
  url: redis://localhost:6379/0
  max_connections: 50

# Trading configuration
trading:
  risk_management:
    max_position_size: 10000
    max_daily_loss: 5000
    stop_loss_percentage: 0.02
  execution:
    slippage_tolerance: 0.001
    timeout_seconds: 30

# Model configuration
models:
  save_path: /opt/xtrade-ai/models
  backup_path: /opt/xtrade-ai/backups
  auto_save_interval: 3600

# Monitoring
monitoring:
  enabled: true
  metrics_port: 9090
  health_check_interval: 60
```

### Load Balancing

#### Nginx Configuration

```nginx
# /etc/nginx/sites-available/xtrade-ai
upstream xtrade_backend {
    least_conn;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://xtrade_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

#### HAProxy Configuration

```haproxy
# /etc/haproxy/haproxy.cfg
global
    daemon
    maxconn 4096

defaults
    mode http
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms

frontend xtrade_frontend
    bind *:80
    default_backend xtrade_backend

backend xtrade_backend
    balance roundrobin
    server xtrade1 127.0.0.1:8001 check
    server xtrade2 127.0.0.1:8002 check
    server xtrade3 127.0.0.1:8003 check
```

### Process Management

#### Systemd Service

```ini
# /etc/systemd/system/xtrade-ai@.service
[Unit]
Description=XTrade-AI Trading Framework Instance %i
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=xtrade
Group=xtrade
WorkingDirectory=/opt/xtrade-ai
Environment=INSTANCE_ID=%i
Environment=CONFIG_FILE=/opt/xtrade-ai/config/production.yaml
ExecStart=/opt/xtrade-ai/venv/bin/python -m xtrade_ai.cli start --config %i
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

#### Supervisor Configuration

```ini
# /etc/supervisor/conf.d/xtrade-ai.conf
[program:xtrade-ai]
command=/opt/xtrade-ai/venv/bin/python -m xtrade_ai.cli start
directory=/opt/xtrade-ai
user=xtrade
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/xtrade-ai/app.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
```

## Configuration Management

### Environment Variables

```bash
# Production environment variables
export XTRADE_ENVIRONMENT=production
export XTRADE_LOG_LEVEL=INFO
export XTRADE_DATABASE_URL=postgresql://user:pass@localhost:5432/xtrade
export XTRADE_REDIS_URL=redis://localhost:6379/0
export XTRADE_MODELS_PATH=/opt/xtrade-ai/models
export XTRADE_DATA_PATH=/opt/xtrade-ai/data
```

### Configuration Files

```yaml
# config/default.yaml
environment: development
log_level: DEBUG
debug: true

# Database
database:
  url: sqlite:///xtrade.db
  pool_size: 5

# Redis
redis:
  url: redis://localhost:6379/0

# Trading
trading:
  risk_management:
    max_position_size: 1000
    max_daily_loss: 500
    stop_loss_percentage: 0.01

# Models
models:
  save_path: ./models
  auto_save_interval: 1800
```

### Secrets Management

#### Using Environment Files

```bash
# .env.production
XTRADE_DATABASE_URL=postgresql://user:pass@localhost:5432/xtrade
XTRADE_API_KEY=your-secret-api-key
XTRADE_BROKER_PASSWORD=your-broker-password
```

#### Using HashiCorp Vault

```python
import hvac

# Initialize Vault client
client = hvac.Client(url='http://localhost:8200')
client.token = 'your-vault-token'

# Get secrets
secrets = client.secrets.kv.v2.read_secret_version(
    path='xtrade-ai/production'
)['data']['data']

# Use secrets
database_url = secrets['database_url']
api_key = secrets['api_key']
```

## Monitoring and Logging

### Logging Configuration

```python
# logging_config.py
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': '/var/log/xtrade-ai/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10
        },
    },
    'loggers': {
        'xtrade_ai': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': False
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console']
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
```

### Metrics Collection

#### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'xtrade-ai'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

#### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "XTrade-AI Metrics",
    "panels": [
      {
        "title": "Trading Performance",
        "type": "graph",
        "targets": [
          {
            "expr": "xtrade_total_pnl",
            "legendFormat": "Total PnL"
          }
        ]
      },
      {
        "title": "Model Accuracy",
        "type": "graph",
        "targets": [
          {
            "expr": "xtrade_model_accuracy",
            "legendFormat": "Accuracy"
          }
        ]
      }
    ]
  }
}
```

### Health Checks

```python
# health_check.py
import requests
import time

def health_check():
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            return True
    except:
        pass
    return False

def main():
    while True:
        if not health_check():
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Health check failed")
        time.sleep(60)

if __name__ == "__main__":
    main()
```

## Security Considerations

### Network Security

```bash
# Firewall configuration (UFW)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp
sudo ufw enable
```

### SSL/TLS Configuration

```nginx
# SSL configuration for Nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass http://xtrade_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Access Control

```python
# access_control.py
from functools import wraps
from flask import request, abort
import jwt

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            abort(401)
        
        try:
            payload = jwt.decode(token, 'your-secret-key', algorithms=['HS256'])
            request.user = payload
        except jwt.InvalidTokenError:
            abort(401)
        
        return f(*args, **kwargs)
    return decorated
```

## Performance Optimization

### Database Optimization

```sql
-- PostgreSQL optimization
CREATE INDEX idx_trades_timestamp ON trades(timestamp);
CREATE INDEX idx_trades_symbol ON trades(symbol);
CREATE INDEX idx_models_created_at ON models(created_at);

-- Partitioning for large tables
CREATE TABLE trades_partitioned (
    LIKE trades INCLUDING ALL
) PARTITION BY RANGE (timestamp);

CREATE TABLE trades_2024 PARTITION OF trades_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

### Caching Strategy

```python
# caching.py
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expire_time=300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return cached_result.decode('utf-8')
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, expire_time, str(result))
            return result
        return wrapper
    return decorator
```

### Resource Limits

```yaml
# Docker resource limits
version: '3.8'
services:
  xtrade-ai:
    image: anasamu7/xtrade-ai:latest
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
    ulimits:
      nofile:
        soft: 65536
        hard: 65536
```

## Troubleshooting

### Common Issues

#### High Memory Usage

```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head -10

# Monitor with htop
htop

# Check for memory leaks
python -m memory_profiler your_script.py
```

#### Database Connection Issues

```bash
# Test database connectivity
psql -h localhost -U user -d xtrade -c "SELECT 1;"

# Check connection pool
SELECT * FROM pg_stat_activity WHERE datname = 'xtrade';
```

#### Performance Bottlenecks

```python
# Profiling with cProfile
import cProfile
import pstats

def profile_function(func, *args, **kwargs):
    profiler = cProfile.Profile()
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()
    
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
    
    return result
```

### Debug Mode

```bash
# Enable debug mode
export XTRADE_DEBUG=true
export XTRADE_LOG_LEVEL=DEBUG

# Run with debug flags
python -m xtrade_ai.cli start --debug --verbose
```

### Log Analysis

```bash
# Search for errors
grep -i error /var/log/xtrade-ai/app.log

# Monitor logs in real-time
tail -f /var/log/xtrade-ai/app.log

# Analyze log patterns
awk '/ERROR/ {print $1, $2}' /var/log/xtrade-ai/app.log | sort | uniq -c
```

This deployment guide provides comprehensive coverage of all deployment scenarios for the XTrade-AI framework. For specific issues or advanced configurations, refer to the troubleshooting section or consult the framework documentation.

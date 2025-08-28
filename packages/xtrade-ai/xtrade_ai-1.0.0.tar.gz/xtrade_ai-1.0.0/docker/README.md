# XTrade-AI Framework Docker Setup

This directory contains Docker configurations for deploying the XTrade-AI Framework using PyPI packages.

## Overview

The Docker setup provides multiple image variants optimized for different use cases:

- **Production**: Full-featured deployment with all dependencies
- **Minimal**: Resource-constrained environments
- **API-Only**: Microservices architecture
- **Development**: Development and debugging environment

## Docker Images

### 1. Main Production Image (`Dockerfile`)

**Base**: `python:3.11-slim`  
**Size**: Medium  
**Features**: Complete framework with all optional dependencies

```bash
# Build
docker build -f docker/Dockerfile -t xtrade-ai:latest .

# Run
docker run -p 8000:8000 xtrade-ai:latest
```

**Installation**: `pip install xtrade-ai[all]`

### 2. Minimal Image (`Dockerfile.minimal`)

**Base**: `python:3.11-alpine`  
**Size**: Small  
**Features**: Basic framework only

```bash
# Build
docker build -f docker/Dockerfile.minimal -t xtrade-ai:minimal .

# Run
docker run -p 8000:8000 xtrade-ai:minimal
```

**Installation**: `pip install xtrade-ai`

### 3. API-Only Image (`Dockerfile.api`)

**Base**: `python:3.11-slim`  
**Size**: Medium  
**Features**: API server with database support

```bash
# Build
docker build -f docker/Dockerfile.api -t xtrade-ai:api .

# Run
docker run -p 8000:8000 xtrade-ai:api
```

**Installation**: `pip install xtrade-ai[api,database]`

### 4. Development Image (`Dockerfile.dev`)

**Base**: `python:3.11-slim`  
**Size**: Large  
**Features**: Development tools and debugging

```bash
# Build
docker build -f docker/Dockerfile.dev -t xtrade-ai:dev .

# Run
docker run -p 8000:8000 -v $(pwd)/xtrade_ai:/app/xtrade_ai xtrade-ai:dev
```

**Installation**: `pip install xtrade-ai[all,dev]`

## Docker Compose

### Quick Start

```bash
# Start all services
cd docker
docker-compose up -d

# Start specific profiles
docker-compose --profile minimal up -d    # Minimal setup
docker-compose --profile api up -d        # API-only setup
docker-compose --profile dev up -d        # Development setup
```

### Services

1. **xtrade-ai**: Main application (port 8000)
2. **xtrade-ai-minimal**: Minimal version (port 8001)
3. **xtrade-ai-api**: API-only version (port 8002)
4. **xtrade-ai-dev**: Development version (port 8003)
5. **postgres**: PostgreSQL database (port 5432)
6. **redis**: Redis cache (port 6379)
7. **nginx**: Reverse proxy (port 80/443)
8. **prometheus**: Monitoring (port 9090)
9. **grafana**: Dashboard (port 3000)

### Environment Variables

```yaml
# Database
POSTGRES_HOST: postgres
POSTGRES_PORT: 5432
POSTGRES_DB: xtrade_ai
POSTGRES_USER: xtrade_user
POSTGRES_PASSWORD: xtrade_password

# Redis
REDIS_HOST: redis
REDIS_PORT: 6379

# Application
XTRADE_DATA_DIR: /app/data
XTRADE_MODEL_DIR: /app/models
XTRADE_LOG_DIR: /app/logs
XTRADE_CONFIG_DIR: /app/config
```

## Build Script

Use the provided build script to build and test all images:

```bash
# Build and test all images
./docker/build.sh

# Clean build (remove existing images first)
./docker/build.sh -c

# Test only (skip building)
./docker/build.sh -t

# Build with specific version
./docker/build.sh -v 1.0.0
```

## Usage Examples

### 1. Production Deployment

```bash
# Pull from Docker Hub
docker pull anasamu7/xtrade-ai:latest

# Run with database
docker run -d \
  --name xtrade-ai \
  -p 8000:8000 \
  -e POSTGRES_HOST=your-db-host \
  -e POSTGRES_PASSWORD=your-password \
  -v /path/to/data:/app/data \
  anasamu7/xtrade-ai:latest
```

### 2. Development Environment

```bash
# Build development image
docker build -f docker/Dockerfile.dev -t xtrade-ai:dev .

# Run with source code mounted
docker run -d \
  --name xtrade-ai-dev \
  -p 8000:8000 \
  -v $(pwd)/xtrade_ai:/app/xtrade_ai \
  -v $(pwd)/data:/app/data \
  xtrade-ai:dev
```

### 3. API-Only Microservice

```bash
# Build API-only image
docker build -f docker/Dockerfile.api -t xtrade-ai:api .

# Run as microservice
docker run -d \
  --name xtrade-ai-api \
  -p 8000:8000 \
  --network microservices \
  xtrade-ai:api
```

### 4. Resource-Constrained Environment

```bash
# Build minimal image
docker build -f docker/Dockerfile.minimal -t xtrade-ai:minimal .

# Run with resource limits
docker run -d \
  --name xtrade-ai-minimal \
  -p 8000:8000 \
  --memory=512m \
  --cpus=0.5 \
  xtrade-ai:minimal
```

## Health Checks

All images include health checks:

```bash
# Check container health
docker ps

# View health check logs
docker inspect --format='{{.State.Health}}' container-name

# Manual health check
curl http://localhost:8000/health
```

## Monitoring

### Prometheus Metrics

```bash
# Access Prometheus
curl http://localhost:9090

# View metrics
curl http://localhost:8000/metrics
```

### Grafana Dashboard

```bash
# Access Grafana
open http://localhost:3000

# Default credentials
Username: admin
Password: admin
```

## Troubleshooting

### Common Issues

1. **Import Error**: Framework not installed from PyPI
   ```bash
   # Check if package is installed
   docker run --rm xtrade-ai:latest pip list | grep xtrade-ai
   ```

2. **Database Connection**: Check environment variables
   ```bash
   # Verify database connection
   docker run --rm xtrade-ai:latest python -c "
   import psycopg2
   conn = psycopg2.connect(host='postgres', database='xtrade_ai', user='xtrade_user', password='xtrade_password')
   print('Database connection successful')
   "
   ```

3. **Port Conflicts**: Check if ports are available
   ```bash
   # Check port usage
   netstat -tulpn | grep :8000
   ```

4. **Permission Issues**: Check file permissions
   ```bash
   # Fix permissions
   sudo chown -R $USER:$USER ./data ./models ./logs
   ```

### Debug Mode

```bash
# Run with debug output
docker run --rm -it xtrade-ai:latest bash

# Check logs
docker logs container-name

# Execute commands in running container
docker exec -it container-name bash
```

## Security

### Best Practices

1. **Non-root User**: All images run as non-root user `xtrade`
2. **Secrets Management**: Use Docker secrets or environment variables
3. **Network Isolation**: Use Docker networks for service communication
4. **Image Scanning**: Regularly scan images for vulnerabilities

### Security Scanning

```bash
# Scan image for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image xtrade-ai:latest
```

## Performance

### Optimization Tips

1. **Multi-stage Builds**: Use for smaller production images
2. **Layer Caching**: Optimize Dockerfile layer order
3. **Resource Limits**: Set appropriate CPU and memory limits
4. **Health Checks**: Implement proper health check endpoints

### Resource Monitoring

```bash
# Monitor container resources
docker stats

# Check image sizes
docker images xtrade-ai
```

## Contributing

### Adding New Images

1. Create new Dockerfile
2. Update build script
3. Add to docker-compose.yml
4. Update documentation

### Testing

```bash
# Run all tests
./docker/build.sh -t

# Test specific image
docker run --rm xtrade-ai:latest python -m pytest
```

## Support

For Docker-related issues:

1. Check the troubleshooting section
2. Review Docker logs
3. Test with minimal configuration
4. Contact maintainer: anasamu7@gmail.com

## License

This Docker setup is part of the XTrade-AI Framework and is licensed under the MIT License.

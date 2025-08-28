# Configuration Directory

This directory contains all configuration files for the XTrade-AI framework.

## Files

### Core Configuration
- `env.example` - Environment variables template
- `init.sql` - Database initialization script

### Web Server Configuration
- `nginx.conf` - Nginx web server configuration
- `prometheus.yml` - Prometheus monitoring configuration

## Usage

### Environment Setup

1. Copy the environment template:
```bash
cp config/env.example .env
```

2. Edit `.env` with your configuration:
```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=xtrade_ai
DB_USER=xtrade_user
DB_PASSWORD=your_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# API
API_HOST=0.0.0.0
API_PORT=8000
```

### Database Setup

The `init.sql` file contains the database schema and initial data:

```bash
# For PostgreSQL
psql -U postgres -d xtrade_ai -f config/init.sql
```

### Web Server Setup

#### Nginx Configuration
The `nginx.conf` file is configured for:
- Reverse proxy to the XTrade-AI API
- Static file serving
- SSL termination (when configured)
- Load balancing

#### Prometheus Monitoring
The `prometheus.yml` file configures:
- Metrics collection from XTrade-AI
- Alerting rules
- Data retention policies

## Docker Integration

When using Docker, these files are automatically mounted:

```yaml
# docker-compose.yml
volumes:
  - ./config/init.sql:/docker-entrypoint-initdb.d/init.sql
  - ./config/nginx.conf:/etc/nginx/nginx.conf:ro
  - ./config/prometheus.yml:/etc/prometheus/prometheus.yml:ro
```

## Security Notes

- Never commit `.env` files with real credentials
- Use environment variables for sensitive data
- Regularly rotate database passwords
- Monitor access logs for security issues

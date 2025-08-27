# XTrade-AI Framework

A comprehensive reinforcement learning framework for algorithmic trading with enhanced error handling, memory management, and thread safety.

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI (recommended)
pip install xtrade-ai

# Or install with specific features
pip install xtrade-ai[ta,monitor,performance]

# Or install from source
git clone https://github.com/anasamu/xtrade-ai-framework.git
cd xtrade-ai-framework
pip install -e .
```

### Basic Usage

```python
from xtrade_ai import XTradeAIFramework, XTradeAIConfig

# Initialize framework
config = XTradeAIConfig()
framework = XTradeAIFramework(config)

# Train model
results = framework.train(training_data, epochs=100)

# Make predictions
decision = framework.predict(market_data)

# Run backtest
backtest_results = framework.backtest(historical_data)
```

### Command Line Interface

```bash
# Train a model
xtrade-ai train --data-path data/training.csv --model-path models/

# Make predictions
xtrade-ai predict --data-path data/market.csv --model-path models/model.pkl

# Run backtest
xtrade-ai backtest --data-path data/historical.csv --output results.json
```

## 🏗️ Production Deployment

### Using Docker Compose

```bash
# Deploy with monitoring
./deploy.sh deploy production with-monitoring

# Or on Windows
.\deploy.ps1 deploy production with-monitoring
```

### Manual Deployment

```bash
# Build and start services
docker-compose up -d

# Start with monitoring
docker-compose --profile monitoring up -d

# Check status
docker-compose ps
```

### Access URLs

- **Main Application**: http://localhost
- **API Documentation**: http://localhost/docs
- **Grafana Dashboard**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

## 📊 Framework Features

### Core Components

- **XTradeAIFramework**: Main orchestrator class
- **Baseline3Integration**: Stable-Baselines3 RL integration
- **XGBoostModule**: Gradient boosting for trading signals
- **RiskManagementModule**: Dynamic risk assessment
- **TechnicalAnalysisModule**: Advanced technical indicators
- **MonitoringModule**: Real-time performance tracking

### Production Features

- **Docker Support**: Complete containerization
- **Database Integration**: PostgreSQL with optimized schema
- **Caching**: Redis for high-performance caching
- **Monitoring**: Prometheus + Grafana stack
- **API**: FastAPI with automatic documentation
- **CLI**: Command-line interface for all operations
- **CI/CD**: GitHub Actions with automated testing
- **Security**: Built-in security headers and rate limiting

### Development Features

- **Error Handling**: Comprehensive error management
- **Memory Management**: Automatic cleanup and optimization
- **Thread Safety**: Multi-threading support
- **Logging**: Structured logging with multiple levels
- **Testing**: Pytest with coverage reporting
- **Code Quality**: Black, flake8, mypy integration

## 🛠️ Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"
```

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Format code
black .
isort .
```

### Available Commands

```bash
# Development
make test          # Run tests
make lint          # Run linting
make format        # Format code
make clean         # Clean build artifacts

# Building
make build         # Build package
make publish       # Publish to PyPI

# Docker
make docker-build  # Build Docker image
make docker-run    # Run Docker container

# Deployment
make deploy        # Deploy with Docker Compose
make deploy-mon    # Deploy with monitoring
```

## 📁 Project Structure

```
xtrade-ai/
├── xtrade_ai/                 # Main package
│   ├── __init__.py           # Package initialization
│   ├── xtrade_ai_framework.py # Main framework class
│   ├── config.py             # Configuration management
│   ├── data_structures.py    # Data models
│   ├── cli.py               # Command-line interface
│   ├── modules/             # Trading modules
│   │   ├── baseline3_integration.py
│   │   ├── xgboost_module.py
│   │   ├── risk_management.py
│   │   └── ...
│   └── utils/               # Utility modules
│       ├── logger.py
│       ├── memory_manager.py
│       ├── thread_manager.py
│       └── ...
├── docker-compose.yml        # Production deployment
├── Dockerfile               # Container definition
├── pyproject.toml           # Package configuration
├── requirements.txt         # Dependencies
├── deploy.sh               # Linux/macOS deployment script
├── deploy.ps1              # Windows deployment script
├── Makefile                # Development commands
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `env.example`:

```bash
# Copy example configuration
cp env.example .env

# Edit configuration
nano .env
```

### Trading Configuration

```yaml
# config/trading.yaml
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

## 📈 Monitoring

### Metrics

The framework provides comprehensive metrics:

- **Trading Metrics**: P&L, win rate, Sharpe ratio, drawdown
- **System Metrics**: CPU, memory, disk usage
- **Model Metrics**: Training progress, prediction accuracy
- **Application Metrics**: Request rates, response times

### Dashboards

Pre-configured Grafana dashboards for:

- Trading Performance Overview
- System Health Monitoring
- Model Performance Tracking
- Risk Metrics Analysis

## 🔒 Security

### Built-in Security Features

- **HTTPS Support**: SSL/TLS encryption
- **Rate Limiting**: API request throttling
- **Security Headers**: XSS protection, CSRF prevention
- **Input Validation**: Comprehensive data validation
- **Access Control**: Role-based permissions

### Security Best Practices

1. Use strong passwords in production
2. Enable HTTPS with valid certificates
3. Configure firewall rules
4. Regular security updates
5. Monitor access logs

## 🚀 Scaling

### Horizontal Scaling

```bash
# Scale the main application
docker-compose up -d --scale xtrade-ai=3

# Use load balancer
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

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=xtrade_ai --cov-report=html

# Run specific test categories
pytest -m "unit"
pytest -m "integration"
pytest -m "not slow"
```

### Test Structure

```
test/
├── test_framework.py      # Framework tests
├── test_modules.py        # Module tests
├── test_utils.py          # Utility tests
├── test_integration.py    # Integration tests
└── conftest.py           # Test configuration
```

## 📚 Documentation

- **API Documentation**: http://localhost/docs (when running)
- **Code Documentation**: Generated with Sphinx
- **User Guide**: See `docs/` directory
- **Development Guide**: See `CONTRIBUTING.md`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

### Development Setup

```bash
# Clone repository
git clone https://github.com/anasamu/xtrade-ai-framework.git
cd xtrade-ai-framework

# Install development dependencies
pip install -e ".[dev]"

# Setup pre-commit hooks
pre-commit install

# Run tests
pytest
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Stable-Baselines3 team for the RL framework
- OpenAI Gymnasium for the environment interface
- The open-source community for various dependencies

## 📞 Support

- **Documentation**: https://xtrade-ai.readthedocs.io
- **Issues**: https://github.com/anasamu/xtrade-ai-framework/issues
- **Discussions**: https://github.com/anasamu/xtrade-ai-framework/discussions
- **Email**: anasamu7@gmail.com

---

**XTrade-AI Framework** - Empowering algorithmic trading with AI 🚀
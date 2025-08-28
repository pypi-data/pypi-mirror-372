# XTrade-AI Framework

[![PyPI version](https://badge.fury.io/py/xtrade-ai.svg)](https://badge.fury.io/py/xtrade-ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A comprehensive reinforcement learning framework for algorithmic trading with enhanced error handling, memory management, and thread safety.

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install xtrade-ai

# Install with optional dependencies
pip install xtrade-ai[ta,dev,viz,monitor,performance,database,api]

# Or install from source
git clone https://github.com/anasamu7/xtrade-ai.git
cd xtrade-ai
pip install -e .
```

### Basic Usage

```python
from xtrade_ai import XTradeAIFramework, XTradeAIConfig

# Create configuration
config = XTradeAIConfig()
config.model.baseline_algorithm = "PPO"
config.trading.initial_balance = 10000.0

# Initialize framework
framework = XTradeAIFramework(config)

# Train the model
framework.train(training_data, epochs=100)

# Make predictions
prediction = framework.predict(market_data)
print(f"Action: {prediction['action']}, Confidence: {prediction['confidence']}")
```

### Command Line Interface

```bash
# Check framework health
xtrade-ai health

# Train a model
xtrade-ai train --config config.yaml --data training_data.csv

# Make predictions
xtrade-ai predict --model model.pkl --data market_data.csv

# Run backtesting
xtrade-ai backtest --model model.pkl --data historical_data.csv

# Start API server
xtrade-ai start-api --host 0.0.0.0 --port 8000
```

## ✨ Features

### 🤖 AI/ML Capabilities
- **Reinforcement Learning**: PPO, DQN, A2C algorithms from Stable-Baselines3
- **Ensemble Learning**: Multi-model predictions with weighted averaging
- **XGBoost Integration**: Gradient boosting for feature selection and prediction
- **Attention Mechanisms**: Transformer-based models for sequence modeling
- **Meta-Learning**: Adaptive learning across different market conditions

### 📊 Trading Features
- **Technical Analysis**: 50+ technical indicators with adaptive parameters
- **Risk Management**: Dynamic position sizing and stop-loss management
- **Portfolio Management**: Multi-asset portfolio optimization
- **Market Simulation**: Realistic market environment simulation
- **Order Management**: Intelligent order placement and execution

### 🔧 Technical Features
- **Thread Safety**: Multi-threaded training and prediction
- **Memory Management**: Automatic memory cleanup and optimization
- **Error Handling**: Comprehensive error handling and recovery
- **Database Integration**: PostgreSQL and Redis support
- **REST API**: FastAPI-based API with authentication
- **Docker Support**: Containerized deployment

### 🌐 API & Integration
- **REST API**: FastAPI-based API with OpenAPI documentation
- **Database Support**: PostgreSQL for data persistence
- **Caching**: Redis for performance optimization
- **Authentication**: API key-based authentication
- **Monitoring**: Comprehensive logging and metrics

## 📦 Installation Options

### Basic Installation
```bash
pip install xtrade-ai
```

### With Technical Analysis
```bash
pip install xtrade-ai[ta]
```

### With Visualization
```bash
pip install xtrade-ai[viz]
```

### With Monitoring
```bash
pip install xtrade-ai[monitor]
```

### With Performance Optimization
```bash
pip install xtrade-ai[performance]
```

### With Database Support
```bash
pip install xtrade-ai[database]
```

### With API Support
```bash
pip install xtrade-ai[api]
```

### Complete Installation
```bash
pip install xtrade-ai[all]
```

## 🔧 Configuration

### Basic Configuration
```python
from xtrade_ai import XTradeAIConfig

config = XTradeAIConfig()
config.model.baseline_algorithm = "PPO"
config.trading.initial_balance = 10000.0
config.trading.commission_rate = 0.001
config.risk.max_position_size = 0.1
```

### Advanced Configuration
```python
config = XTradeAIConfig()

# Model configuration
config.model.baseline_algorithm = "PPO"
config.model.learning_rate = 0.0003
config.model.batch_size = 64
config.model.buffer_size = 1000000

# Trading configuration
config.trading.initial_balance = 10000.0
config.trading.commission_rate = 0.001
config.trading.slippage = 0.0001
config.trading.max_positions = 5

# Risk management
config.risk.max_position_size = 0.1
config.risk.stop_loss = 0.02
config.risk.take_profit = 0.04
config.risk.max_drawdown = 0.15
```

## 📚 Examples

### Training a Model
```python
from xtrade_ai import XTradeAIFramework, XTradeAIConfig
import pandas as pd

# Load data
data = pd.read_csv('market_data.csv')

# Configure framework
config = XTradeAIConfig()
config.model.baseline_algorithm = "PPO"
config.trading.initial_balance = 10000.0

# Initialize and train
framework = XTradeAIFramework(config)
framework.train(data, epochs=100)

# Save model
framework.save_model("models/my_model")
```

### Making Predictions
```python
# Load trained model
framework = XTradeAIFramework.load_model("models/my_model")

# Prepare market data
market_data = pd.read_csv('current_market_data.csv')

# Make prediction
prediction = framework.predict(market_data)
print(f"Action: {prediction['action']}")
print(f"Confidence: {prediction['confidence']}")
print(f"Position Size: {prediction['position_size']}")
```

### Using the API
```python
import requests

# Start API server
# xtrade-ai start-api --host 0.0.0.0 --port 8000

# Make API request
response = requests.post(
    "http://localhost:8000/predict",
    headers={"Authorization": "Bearer your-api-key"},
    json={
        "market_data": market_data.to_dict(),
        "model_id": "my_model"
    }
)

result = response.json()
print(f"Prediction: {result}")
```

## 🐳 Docker Deployment

### Quick Start
```bash
# Pull the image
docker pull anasamu7/xtrade-ai:latest

# Run the API server
docker run -p 8000:8000 anasamu7/xtrade-ai:latest
```

### With Docker Compose
```bash
# Clone repository
git clone https://github.com/anasamu7/xtrade-ai.git
cd xtrade-ai

# Start services
docker-compose up -d
```

## 📊 Monitoring and Logging

### Health Check
```bash
# Check framework health
xtrade-ai health

# Check API health
curl http://localhost:8000/health
```

### Logging
```python
import logging
from xtrade_ai.utils.logger import get_logger

# Get logger
logger = get_logger(__name__)

# Log messages
logger.info("Training started")
logger.warning("High memory usage detected")
logger.error("Training failed")
```

## 🔒 Security

### API Authentication
```python
# Create API key
xtrade-ai api create-key --username admin --password admin123 --key-name my-key

# Use API key
headers = {"Authorization": "Bearer your-api-key"}
response = requests.get("http://localhost:8000/models", headers=headers)
```

### Database Security
- Encrypted connections
- Role-based access control
- API request logging
- Rate limiting

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install xtrade-ai[dev]

# Run all tests
pytest

# Run specific tests
pytest test/test_training.py
pytest test/test_api.py
```

### Test Build
```bash
# Test build process
python scripts/test_build.py

# Build package
python -m build

# Check package
twine check dist/*
```

## 📈 Performance

### Optimization Tips
1. Use GPU acceleration for training
2. Enable memory optimization
3. Use caching for repeated operations
4. Optimize data preprocessing
5. Use appropriate batch sizes

### Benchmarking
```python
from xtrade_ai.utils.performance_monitor import PerformanceMonitor

monitor = PerformanceMonitor()
monitor.start_timer("training")

# Your training code here
framework.train(data, epochs=100)

monitor.end_timer("training")
print(f"Training time: {monitor.get_timer('training')}")
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Clone repository
git clone https://github.com/anasamu7/xtrade-ai.git
cd xtrade-ai

# Install development dependencies
pip install -e .[dev]

# Setup pre-commit hooks
pre-commit install

# Run tests
pytest
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation
- [User Guide](https://xtrade-ai.readthedocs.io/)
- [API Reference](https://xtrade-ai.readthedocs.io/en/latest/api_reference.html)
- [Examples](https://xtrade-ai.readthedocs.io/en/latest/examples.html)

### Community
- [GitHub Issues](https://github.com/anasamu7/xtrade-ai/issues)
- [GitHub Discussions](https://github.com/anasamu7/xtrade-ai/discussions)
- [Email Support](mailto:anasamu7@gmail.com)

### Troubleshooting
- [FAQ](https://xtrade-ai.readthedocs.io/en/latest/faq.html)
- [Troubleshooting Guide](https://xtrade-ai.readthedocs.io/en/latest/troubleshooting.html)

## 🔗 Links

- **Homepage**: https://github.com/anasamu7/xtrade-ai
- **Documentation**: https://xtrade-ai.readthedocs.io/
- **PyPI**: https://pypi.org/project/xtrade-ai/
- **Docker Hub**: https://hub.docker.com/r/anasamu7/xtrade-ai
- **Issues**: https://github.com/anasamu7/xtrade-ai/issues
- **Releases**: https://github.com/anasamu7/xtrade-ai/releases

---

**Note**: This framework is for educational and research purposes. Always test thoroughly before using in production trading environments.

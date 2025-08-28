# XTrade-AI Framework User Guide

## Table of Contents

- [Getting Started](#getting-started)
- [Installation Guide](#installation-guide)
- [Quick Start Tutorial](#quick-start-tutorial)
- [Data Preparation](#data-preparation)
- [Model Training](#model-training)
- [Making Predictions](#making-predictions)
- [Backtesting](#backtesting)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Getting Started

### What is XTrade-AI Framework?

XTrade-AI Framework is a comprehensive reinforcement learning framework designed for algorithmic trading. It combines multiple AI/ML approaches including:

- **Reinforcement Learning**: PPO, DQN, A2C algorithms
- **Machine Learning**: XGBoost for feature selection and prediction
- **Technical Analysis**: 50+ technical indicators
- **Risk Management**: Dynamic position sizing and stop-loss
- **Ensemble Learning**: Multi-model predictions

### Key Features

- 🚀 **Easy to Use**: Simple API for training and prediction
- 🧠 **Multiple Algorithms**: Support for various RL and ML algorithms
- 📊 **Technical Analysis**: Built-in technical indicators
- 🛡️ **Risk Management**: Automatic risk assessment and position sizing
- 🔄 **Ensemble Learning**: Combine multiple models for better predictions
- 📈 **Backtesting**: Comprehensive backtesting capabilities
- 🛠️ **Modular Design**: Easy to customize and extend

## Installation Guide

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (for development installation)

### Basic Installation

```bash
# Install from PyPI
pip install xtrade-ai
```

### Advanced Installation

```bash
# Install with all optional dependencies
pip install xtrade-ai[all]

# Install specific feature sets
pip install xtrade-ai[ta]      # Technical analysis
pip install xtrade-ai[dev]      # Development tools
pip install xtrade-ai[viz]      # Visualization
pip install xtrade-ai[monitor]  # Monitoring
pip install xtrade-ai[api]      # API server
```

### Docker Installation

```bash
# Pull from Docker Hub
docker pull anasamu7/xtrade-ai:latest

# Run container
docker run -it anasamu7/xtrade-ai:latest xtrade-ai --help
```

### Verification

After installation, verify that everything is working:

```python
from xtrade_ai import XTradeAIFramework, XTradeAIConfig, health_check

# Check framework health
status = health_check()
print(f"Framework status: {status['overall_status']}")

# Create basic configuration
config = XTradeAIConfig()
print("Configuration created successfully!")
```

## Quick Start Tutorial

### Step 1: Prepare Your Data

First, prepare your market data in the correct format:

```python
import pandas as pd

# Load your market data
data = pd.read_csv('market_data.csv')

# Ensure you have the required columns
required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
print(f"Data columns: {list(data.columns)}")
print(f"Data shape: {data.shape}")
```

**Data Format Requirements:**
- **timestamp**: DateTime index or column
- **open**: Opening price
- **high**: Highest price
- **low**: Lowest price
- **close**: Closing price
- **volume**: Trading volume

### Step 2: Create Configuration

```python
from xtrade_ai import XTradeAIConfig

# Create configuration
config = XTradeAIConfig()

# Configure model parameters
config.model.baseline_algorithm = "PPO"  # PPO, DQN, or A2C
config.model.learning_rate = 3e-4
config.model.batch_size = 64

# Configure trading parameters
config.trading.initial_balance = 10000.0
config.trading.commission_rate = 0.001
config.trading.max_position_size = 0.1

# Configure data parameters
config.data.lookback_window = 100
config.data.feature_columns = ["open", "high", "low", "close", "volume"]
config.data.target_column = "returns"

print("Configuration created successfully!")
```

### Step 3: Initialize Framework

```python
from xtrade_ai import XTradeAIFramework

# Initialize framework
framework = XTradeAIFramework(config)

print("Framework initialized successfully!")
```

### Step 4: Train the Model

```python
# Train the model
results = framework.train(
    data=data,
    epochs=100,
    validation_split=0.2
)

print(f"Training completed!")
print(f"Final loss: {results['final_loss']:.4f}")
print(f"Validation accuracy: {results['validation_accuracy']:.2%}")
```

### Step 5: Make Predictions

```python
# Prepare new market data for prediction
new_data = pd.read_csv('new_market_data.csv')

# Make prediction
prediction = framework.predict(new_data)

print(f"Action: {prediction['action']}")
print(f"Confidence: {prediction['confidence']:.2%}")
print(f"Model weights: {prediction['weights']}")
```

### Step 6: Run Backtesting

```python
# Run backtesting on historical data
backtest_results = framework.backtest(
    data=historical_data,
    initial_balance=10000.0,
    commission_rate=0.001
)

print(f"Total Return: {backtest_results['total_return']:.2%}")
print(f"Sharpe Ratio: {backtest_results['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {backtest_results['max_drawdown']:.2%}")
print(f"Win Rate: {backtest_results['win_rate']:.2%}")
```

## Data Preparation

### Data Format

Your market data should be in the following format:

```python
import pandas as pd

# Example data structure
data = pd.DataFrame({
    'timestamp': pd.date_range('2023-01-01', periods=1000, freq='1H'),
    'open': [100.0, 101.0, 102.0, ...],
    'high': [101.5, 102.5, 103.5, ...],
    'low': [99.5, 100.5, 101.5, ...],
    'close': [101.0, 102.0, 103.0, ...],
    'volume': [1000, 1200, 1100, ...]
})

# Set timestamp as index
data.set_index('timestamp', inplace=True)
```

### Data Quality Checks

```python
from xtrade_ai import DataPreprocessor

# Create preprocessor
preprocessor = DataPreprocessor(config)

# Validate data
validation_result = preprocessor.validate_data(data)
print(f"Data validation: {validation_result['is_valid']}")

if not validation_result['is_valid']:
    print(f"Validation errors: {validation_result['errors']}")
```

### Feature Engineering

The framework automatically adds technical indicators:

```python
# Add technical indicators
data_with_indicators = preprocessor.add_technical_indicators(data)

# Check available indicators
print(f"Available indicators: {list(data_with_indicators.columns)}")
```

**Available Technical Indicators:**
- Moving Averages (SMA, EMA, WMA)
- Oscillators (RSI, MACD, Stochastic)
- Volatility (Bollinger Bands, ATR)
- Volume (OBV, VWAP)
- Momentum (ROC, Williams %R)
- And many more...

### Data Normalization

```python
# Normalize features
normalized_data = preprocessor.normalize_features(data_with_indicators)

print("Data normalized successfully!")
```

## Model Training

### Basic Training

```python
# Basic training
results = framework.train(
    data=training_data,
    epochs=100,
    validation_split=0.2
)
```

### Advanced Training Options

```python
# Advanced training with custom parameters
results = framework.train(
    data=training_data,
    epochs=200,
    validation_split=0.2,
    early_stopping_patience=10,
    model_checkpoint_freq=50,
    verbose=True
)
```

### Training with Multiple Algorithms

```python
# Enable ensemble learning
config.model.enable_ensemble = True
config.model.ensemble_method = "weighted_average"

# Train multiple models
results = framework.train_ensemble(
    data=training_data,
    models=['PPO', 'DQN', 'XGBoost'],
    epochs=100
)
```

### Training Progress Monitoring

```python
# Monitor training progress
for epoch in range(100):
    results = framework.train_epoch(data, epoch)
    
    if epoch % 10 == 0:
        print(f"Epoch {epoch}: Loss = {results['loss']:.4f}, "
              f"Accuracy = {results['accuracy']:.2%}")
```

### Model Validation

```python
# Validate model performance
validation_results = framework.validate(
    data=validation_data,
    metrics=['accuracy', 'precision', 'recall', 'f1']
)

print(f"Validation Results:")
for metric, value in validation_results.items():
    print(f"  {metric}: {value:.4f}")
```

## Making Predictions

### Single Prediction

```python
# Make single prediction
prediction = framework.predict(market_data)

print(f"Action: {prediction['action']}")
print(f"Confidence: {prediction['confidence']:.2%}")
print(f"Timestamp: {prediction['timestamp']}")
```

### Batch Predictions

```python
# Make batch predictions
predictions = framework.predict_batch(market_data_batch)

for i, pred in enumerate(predictions):
    print(f"Prediction {i}: Action={pred['action']}, "
          f"Confidence={pred['confidence']:.2%}")
```

### Ensemble Predictions

```python
# Make ensemble prediction
ensemble_prediction = framework.predict_ensemble(market_data)

print(f"Ensemble Action: {ensemble_prediction['action']}")
print(f"Ensemble Confidence: {ensemble_prediction['confidence']:.2%}")
print(f"Model Weights: {ensemble_prediction['weights']}")
```

### Real-time Predictions

```python
import time

# Real-time prediction loop
while True:
    # Get latest market data
    latest_data = get_latest_market_data()
    
    # Make prediction
    prediction = framework.predict(latest_data)
    
    # Execute trade if confidence is high
    if prediction['confidence'] > 0.7:
        execute_trade(prediction['action'])
    
    # Wait for next update
    time.sleep(60)  # 1 minute
```

## Backtesting

### Basic Backtesting

```python
# Basic backtesting
results = framework.backtest(
    data=historical_data,
    initial_balance=10000.0
)
```

### Advanced Backtesting

```python
# Advanced backtesting with custom parameters
results = framework.backtest(
    data=historical_data,
    initial_balance=10000.0,
    commission_rate=0.001,
    slippage=0.0001,
    max_position_size=0.1,
    stop_loss_pct=0.02,
    take_profit_pct=0.05
)
```

### Backtesting Results Analysis

```python
# Analyze backtesting results
print(f"Performance Metrics:")
print(f"  Total Return: {results['total_return']:.2%}")
print(f"  Annualized Return: {results['annualized_return']:.2%}")
print(f"  Sharpe Ratio: {results['sharpe_ratio']:.2f}")
print(f"  Max Drawdown: {results['max_drawdown']:.2%}")
print(f"  Win Rate: {results['win_rate']:.2%}")
print(f"  Profit Factor: {results['profit_factor']:.2f}")
print(f"  Total Trades: {results['total_trades']}")
print(f"  Average Trade: {results['average_trade']:.2f}")

# Plot results
framework.plot_backtest_results(results)
```

### Walk-Forward Analysis

```python
# Walk-forward analysis
walk_forward_results = framework.walk_forward_analysis(
    data=historical_data,
    window_size=252,  # 1 year
    step_size=63,     # 3 months
    initial_balance=10000.0
)

print(f"Walk-forward analysis completed!")
print(f"Average return: {walk_forward_results['average_return']:.2%}")
print(f"Return consistency: {walk_forward_results['return_consistency']:.2%}")
```

## Advanced Features

### Custom Reward Functions

```python
def custom_reward_function(state, action, next_state, reward):
    """Custom reward function"""
    # Add your custom reward logic here
    custom_reward = reward * 1.5  # Amplify rewards
    return custom_reward

# Set custom reward function
framework.set_reward_function(custom_reward_function)
```

### Custom Trading Strategies

```python
from xtrade_ai import BaseEnvironment

class CustomTradingEnvironment(BaseEnvironment):
    def __init__(self, data, config):
        super().__init__(data, config)
        # Add custom logic here
    
    def step(self, action):
        # Custom step logic
        return super().step(action)
    
    def reset(self):
        # Custom reset logic
        return super().reset()

# Use custom environment
custom_env = CustomTradingEnvironment(data, config)
framework.train_with_environment(custom_env, epochs=100)
```

### Multi-Asset Trading

```python
# Configure multi-asset trading
config.trading.assets = ['BTC/USD', 'ETH/USD', 'AAPL', 'GOOGL']
config.trading.correlation_threshold = 0.7

# Train multi-asset model
results = framework.train_multi_asset(
    data_dict={
        'BTC/USD': btc_data,
        'ETH/USD': eth_data,
        'AAPL': aapl_data,
        'GOOGL': googl_data
    },
    epochs=100
)
```

### Meta-Learning

```python
# Enable meta-learning
config.model.enable_meta_learning = True
config.model.meta_learning_rate = 0.01

# Train with meta-learning
results = framework.train_with_meta_learning(
    training_data=training_data,
    meta_data=meta_data,
    epochs=100
)
```

### Hyperparameter Optimization

```python
# Optimize hyperparameters
optimization_results = framework.optimize_hyperparameters(
    data=training_data,
    param_space={
        'learning_rate': [1e-4, 3e-4, 1e-3],
        'batch_size': [32, 64, 128],
        'hidden_dim': [64, 128, 256]
    },
    n_trials=50
)

print(f"Best parameters: {optimization_results['best_params']}")
print(f"Best score: {optimization_results['best_score']:.4f}")
```

## Troubleshooting

### Common Issues

#### Import Errors

```bash
# Check dependencies
xtrade-ai health

# Install missing dependencies
pip install -r requirements.txt
```

#### Memory Issues

```python
# Reduce batch size
config.model.batch_size = 32

# Enable memory cleanup
config.performance.enable_memory_cleanup = True

# Use memory-efficient training
framework.train_memory_efficient(data, epochs=100)
```

#### Training Issues

```python
# Check data quality
framework.validate_data(data)

# Adjust learning rate
config.model.learning_rate = 1e-4

# Enable early stopping
config.training.early_stopping_patience = 5
```

#### Prediction Issues

```python
# Check model state
model_info = framework.get_model_info()
print(f"Model states: {model_info}")

# Reload model if needed
framework = XTradeAIFramework.load_model('model.pkl')
```

### Debug Mode

```python
# Enable debug mode
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with debug information
framework.train(data, epochs=100, debug=True)
```

### Performance Profiling

```python
# Enable performance profiling
config.performance.enable_profiling = True

# Profile training
framework.train_with_profiling(data, epochs=100)
```

## Best Practices

### Data Management

1. **Use High-Quality Data**: Ensure your data is clean and complete
2. **Proper Time Alignment**: Align timestamps across different data sources
3. **Feature Engineering**: Create meaningful features for your trading strategy
4. **Data Validation**: Always validate data before training

### Model Training

1. **Start Simple**: Begin with basic models before adding complexity
2. **Cross-Validation**: Use cross-validation to assess model performance
3. **Hyperparameter Tuning**: Optimize hyperparameters systematically
4. **Regular Retraining**: Retrain models periodically with new data

### Risk Management

1. **Position Sizing**: Use appropriate position sizes based on risk
2. **Stop Losses**: Implement stop-loss mechanisms
3. **Diversification**: Don't put all your capital in one strategy
4. **Monitoring**: Continuously monitor model performance

### Performance Optimization

1. **Memory Management**: Monitor and optimize memory usage
2. **Parallel Processing**: Use parallel processing for large datasets
3. **Caching**: Cache frequently accessed data
4. **GPU Acceleration**: Use GPU acceleration when available

### Testing and Validation

1. **Backtesting**: Always backtest your strategies thoroughly
2. **Walk-Forward Analysis**: Use walk-forward analysis for realistic performance assessment
3. **Out-of-Sample Testing**: Test on unseen data
4. **Stress Testing**: Test under various market conditions

### Production Deployment

1. **Gradual Deployment**: Deploy strategies gradually
2. **Monitoring**: Implement comprehensive monitoring
3. **Error Handling**: Implement robust error handling
4. **Backup Systems**: Have backup systems in place

### Documentation and Maintenance

1. **Documentation**: Document your strategies and configurations
2. **Version Control**: Use version control for code and models
3. **Regular Updates**: Keep the framework and dependencies updated
4. **Performance Tracking**: Track performance over time

## Getting Help

### Documentation

- **API Reference**: Complete API documentation
- **Architecture Guide**: Technical architecture details
- **Examples**: Code examples and tutorials

### Support Channels

- **GitHub Issues**: Report bugs and request features
- **Email Support**: anasamu7@gmail.com
- **Community**: Join the community discussions

### Contributing

We welcome contributions! Please see our contributing guide for details on how to:

- Report bugs
- Request features
- Submit code changes
- Improve documentation

---

**Disclaimer**: This framework is for educational and research purposes. Trading involves risk, and past performance does not guarantee future results. Always perform thorough testing before using in live trading.

# YFinance Integration for XTrade-AI Framework

## Overview

XTrade-AI Framework now includes comprehensive YFinance integration, allowing you to download and process market data directly from Yahoo Finance. This feature provides a unified interface for multiple data sources including YFinance, CSV files, and variable data.

## 🚀 New Features

### 1. YFinance Data Download
- Download real-time and historical market data
- Support for multiple symbols and timeframes
- Automatic data caching for performance
- Comprehensive error handling

### 2. Multiple Data Sources
- **YFinance**: Direct market data download
- **CSV Files**: Load local CSV data files
- **Variable Data**: Process pandas DataFrames directly
- **MetaTrader5**: Integration with existing MT5 setup

### 3. Unified Data Processing
- Standardized column naming across all sources
- Automatic data validation and cleaning
- Seamless integration with existing preprocessing pipeline

## 📦 Installation

The YFinance integration is included in the main XTrade-AI package. No additional installation is required:

```bash
pip install xtrade-ai
```

## 🎯 Quick Start

### Download Data from Yahoo Finance

```python
from xtrade_ai import XTradeAIFramework, XTradeAIConfig

# Initialize framework
config = XTradeAIConfig()
framework = XTradeAIFramework(config)

# Download data from Yahoo Finance
market_data = framework.load_yfinance_data(
    symbols=["AAPL", "GOOGL", "MSFT"],
    start_date="2023-01-01",
    end_date="2023-12-31",
    interval="1d"
)

print(f"Downloaded {len(market_data)} records")
```

### Load Data from CSV

```python
# Load data from CSV file
market_data = framework.load_csv_data(file_path="market_data.csv")
```

### Process Variable Data

```python
import pandas as pd

# Create sample data
sample_data = pd.DataFrame({
    'open': [100, 101, 102],
    'high': [101, 102, 103],
    'low': [99, 100, 101],
    'close': [100.5, 101.5, 102.5],
    'volume': [1000, 1100, 1200]
})

# Process variable data
processed_data = framework.load_variable_data(data=sample_data)
```

## 🛠️ CLI Commands

### Download YFinance Data

```bash
# Download data from Yahoo Finance
xtrade-ai download-yfinance \
  --symbols "AAPL,GOOGL,MSFT" \
  --start-date "2023-01-01" \
  --end-date "2023-12-31" \
  --interval "1d" \
  --output-path "./yfinance_data.csv"
```

### Process Data from Multiple Sources

```bash
# Process data from YFinance
xtrade-ai process-data \
  --source "yfinance" \
  --symbols "AAPL" \
  --start-date "2023-01-01" \
  --end-date "2023-12-31" \
  --output-path "./processed_data.csv"

# Process data from CSV
xtrade-ai process-data \
  --source "csv" \
  --file-path "./market_data.csv" \
  --output-path "./processed_data.csv"
```

## 📊 Supported Data Types

### Stock Symbols
- **US Stocks**: `AAPL`, `GOOGL`, `MSFT`, `AMZN`, `TSLA`
- **ETFs**: `SPY`, `QQQ`, `IWM`, `GLD`, `SLV`
- **Indices**: `^GSPC`, `^DJI`, `^IXIC`

### Forex Symbols
- **Major Pairs**: `EURUSD=X`, `GBPUSD=X`, `USDJPY=X`
- **Cross Pairs**: `EURGBP=X`, `GBPJPY=X`

### Cryptocurrency
- **Bitcoin**: `BTC-USD`
- **Ethereum**: `ETH-USD`
- **Other**: `ADA-USD`, `DOT-USD`

## ⏱️ Data Intervals

| Interval | Description | Time Limit |
|----------|-------------|------------|
| `1m` | 1 minute | 7 days |
| `2m` | 2 minutes | 60 days |
| `5m` | 5 minutes | 60 days |
| `15m` | 15 minutes | 60 days |
| `30m` | 30 minutes | 60 days |
| `60m` | 1 hour | 730 days |
| `90m` | 1.5 hours | 60 days |
| `1h` | 1 hour | 730 days |
| `1d` | 1 day | Unlimited |
| `5d` | 5 days | Unlimited |
| `1wk` | 1 week | Unlimited |
| `1mo` | 1 month | Unlimited |
| `3mo` | 3 months | Unlimited |

## ⚙️ Configuration

### DataSourceConfig

Configure data source settings in your configuration:

```python
from xtrade_ai.config import XTradeAIConfig

config = XTradeAIConfig()

# Configure data source settings
config.data_source.default_source = "yfinance"
config.data_source.yfinance_cache_size = 100
config.data_source.yfinance_timeout = 30
config.data_source.csv_encoding = "utf-8"
config.data_source.enable_cache = True
config.data_source.cache_dir = "./cache"
```

### YAML Configuration

```yaml
data_source:
  default_source: "yfinance"
  yfinance_cache_size: 100
  yfinance_timeout: 30
  csv_encoding: "utf-8"
  enable_cache: true
  cache_dir: "./cache"
```

## 🔄 Complete Training Pipeline

```python
from xtrade_ai import XTradeAIFramework, XTradeAIConfig
from xtrade_ai.data_preprocessor import DataPreprocessor

# 1. Initialize framework
config = XTradeAIConfig()
framework = XTradeAIFramework(config)

# 2. Download data from Yahoo Finance
market_data = framework.load_yfinance_data(
    symbols=["AAPL"],
    start_date="2023-01-01",
    end_date="2023-12-31",
    interval="1d"
)

# 3. Preprocess data
preprocessor = DataPreprocessor(config.to_dict())
processed_data = preprocessor.preprocess_data(market_data)

# 4. Train model
training_data = processed_data.values
results = framework.train(
    data=training_data,
    epochs=100,
    validation_split=0.2
)

print(f"Training completed: {results}")
```

## 📈 Examples

### Real-time Data Updates

```python
# Download recent data
recent_data = framework.load_yfinance_data(
    symbols=["AAPL"],
    period="5d",  # Last 5 days
    interval="1h"  # Hourly data
)

# Process and make predictions
processed_data = preprocessor.preprocess_data(recent_data)
predictions = framework.predict(processed_data.values)
```

### Multiple Data Sources

```python
# Combine data from multiple sources
yfinance_data = framework.load_yfinance_data(
    symbols=["AAPL"],
    start_date="2023-01-01",
    end_date="2023-06-30"
)

csv_data = framework.load_csv_data(file_path="additional_data.csv")

# Combine datasets
combined_data = pd.concat([yfinance_data, csv_data])
processed_data = preprocessor.preprocess_data(combined_data)
```

### Batch Symbol Download

```python
# Download multiple symbols at once
symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
market_data = framework.load_yfinance_data(
    symbols=symbols,
    start_date="2023-01-01",
    end_date="2023-12-31",
    interval="1d"
)

print(f"Downloaded data for {len(symbols)} symbols")
print(f"Data shape: {market_data.shape}")
```

## 🧪 Testing

Run the test suite to verify the integration:

```bash
# Run all tests
python -m pytest test/test_yfinance_integration.py -v

# Run specific test class
python -m pytest test/test_yfinance_integration.py::TestDataSourceManager -v

# Run with coverage
python -m pytest test/test_yfinance_integration.py --cov=xtrade_ai.modules.data_source_manager
```

## 🔧 API Reference

### DataSourceManager

The main class for managing data sources.

#### Methods

- `load_data(source, **kwargs)`: Load data from specified source
- `load_yfinance_data(symbols, start_date, end_date, interval, period, **kwargs)`: Load from Yahoo Finance
- `load_csv_data(file_path, **kwargs)`: Load from CSV file
- `load_variable_data(data, **kwargs)`: Load from DataFrame
- `get_available_symbols(query)`: Get available symbols
- `clear_cache()`: Clear YFinance cache
- `get_cache_info()`: Get cache information

### XTradeAIFramework

Framework methods for data loading:

- `load_data(source, **kwargs)`: Unified data loading
- `load_yfinance_data(symbols, start_date, end_date, interval, period, **kwargs)`: YFinance loading
- `load_csv_data(file_path, **kwargs)`: CSV loading
- `load_variable_data(data, **kwargs)`: Variable data loading

## 🚨 Error Handling

The framework includes comprehensive error handling:

```python
try:
    market_data = framework.load_yfinance_data(
        symbols=["INVALID_SYMBOL"],
        start_date="2023-01-01",
        end_date="2023-12-31"
    )
except ValueError as e:
    print(f"Invalid symbol: {e}")
except Exception as e:
    print(f"Download failed: {e}")
```

## 💾 Caching

YFinance data is automatically cached to improve performance:

```python
# Check cache info
cache_info = framework.data_source_manager.get_cache_info()
print(f"Cache size: {cache_info['cache_size']}")

# Clear cache
framework.data_source_manager.clear_cache()
```

## 🔍 Debug Mode

Enable verbose logging for debugging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Initialize framework with debug logging
config = XTradeAIConfig()
config.log_level = "DEBUG"
framework = XTradeAIFramework(config)
```

## 📚 Documentation

- [YFinance Integration Guide](docs/yfinance_integration.md)
- [API Reference](docs/api_reference.md)
- [Examples](examples/yfinance_integration.py)
- [Configuration Guide](docs/configuration.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/your-repo/xtrade-ai.git
cd xtrade-ai

# Install development dependencies
pip install -r requirements/dev.txt

# Run tests
python -m pytest test/test_yfinance_integration.py -v
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-repo/xtrade-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/xtrade-ai/discussions)

## 🔄 Changelog

### Version 1.0.0
- ✨ Added YFinance integration
- ✨ Added DataSourceManager for unified data loading
- ✨ Added support for CSV and variable data sources
- ✨ Added CLI commands for data download and processing
- ✨ Added comprehensive error handling and caching
- ✨ Added configuration options for data sources
- ✨ Added test suite for all new features
- 📚 Added documentation and examples

## 🙏 Acknowledgments

- [YFinance](https://github.com/ranaroussi/yfinance) - Yahoo Finance market data downloader
- [Pandas](https://pandas.pydata.org/) - Data manipulation and analysis
- [NumPy](https://numpy.org/) - Numerical computing

---

**Happy Trading! 🚀📈**

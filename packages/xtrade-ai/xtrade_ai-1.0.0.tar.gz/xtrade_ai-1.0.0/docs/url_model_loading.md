# URL Model Loading in XTrade-AI Framework

The XTrade-AI framework now supports loading models from various URL sources, making it easy to distribute and deploy models across different environments and cloud platforms.

## Overview

The URL model loading feature allows you to:

- Load models from HTTP/HTTPS URLs
- Download models from S3 buckets
- Access models stored in Google Cloud Storage
- Retrieve models from Azure Blob Storage
- Use local file paths (for compatibility)
- Cache downloaded models for improved performance
- Handle encrypted models with password protection

## Supported URL Schemes

| Scheme | Description | Example |
|--------|-------------|---------|
| `http://` | HTTP URLs | `http://example.com/models/trading_model.models` |
| `https://` | HTTPS URLs | `https://api.example.com/models/forex_model.models` |
| `s3://` | Amazon S3 | `s3://my-bucket/models/crypto_trader.models` |
| `gs://` | Google Cloud Storage | `gs://my-bucket/models/forex_model.models` |
| `azure://` | Azure Blob Storage | `azure://account.blob.core.windows.net/container/model.models` |
| `file://` | Local files | `file:///path/to/local/model.models` |
| (none) | Local files | `/path/to/local/model.models` |

## Configuration

### Persistence Configuration

The URL model loading behavior is controlled by the `PersistenceConfig` in your configuration:

```python
from xtrade_ai import XTradeAIConfig

config = XTradeAIConfig()

# Configure URL loading settings
config.persistence.url_timeout = 300        # Timeout in seconds
config.persistence.url_retries = 3          # Number of retry attempts
config.persistence.url_chunk_size = 8192    # Download chunk size
config.persistence.cache_dir = "./cache"    # Cache directory
config.persistence.enable_cache = True      # Enable caching
config.persistence.cache_expiry = 24        # Cache expiry in hours
```

### Environment Variables

For cloud storage access, you may need to set environment variables:

**AWS S3:**
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

**Google Cloud Storage:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

**Azure Blob Storage:**
```bash
export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=account;AccountKey=key;EndpointSuffix=core.windows.net"
```

## Usage

### Basic URL Model Loading

```python
from xtrade_ai import XTradeAIFramework, XTradeAIConfig

# Initialize framework
config = XTradeAIConfig()
framework = XTradeAIFramework(config)

# Load model from URL
success = framework.load_model("https://example.com/models/trading_model.models")
if success:
    print("Model loaded successfully!")
```

### Loading Encrypted Models

```python
# Load encrypted model with password
success = framework.load_model(
    "https://example.com/models/encrypted_model.models",
    password="my_secret_password"
)
```

### Using URLModelLoader Directly

For more control over the download process:

```python
from xtrade_ai.utils.url_model_loader import URLModelLoader

# Initialize URL loader
url_loader = URLModelLoader(config)

# Download model
downloaded_path = url_loader.load_model_from_url(
    "s3://my-bucket/models/trading_model.models"
)
print(f"Model downloaded to: {downloaded_path}")

# Get cache information
cache_info = url_loader.get_cache_info()
print(f"Cache contains {cache_info['file_count']} files")
```

## CLI Commands

### URL Model Management

The framework provides CLI commands for URL-based model management:

```bash
# Download model from URL
xtrade-ai url load --url https://example.com/models/model.models

# Download with password
xtrade-ai url load --url https://example.com/models/encrypted_model.models --password secret

# Download to specific path
xtrade-ai url load --url s3://bucket/model.models --output-path ./my_model.models

# View cache information
xtrade-ai url cache --action info

# Clear cache
xtrade-ai url cache --action clear
```

### Enhanced CLI Commands

All existing CLI commands now support URL-based model loading:

```bash
# Predict using model from URL
xtrade-ai predict --data-path data.csv --model-path https://example.com/models/model.models

# Backtest using model from S3
xtrade-ai backtest --data-path data.csv --model-path s3://bucket/model.models

# List models from URL
xtrade-ai model list --model-path https://example.com/models/

# Get model info from URL
xtrade-ai model info model_name --model-path gs://bucket/models/
```

## Caching

### Automatic Caching

Models downloaded from URLs are automatically cached to improve performance:

- **Cache Location**: `./cache` (configurable)
- **Cache Key**: MD5 hash of the URL
- **Cache Expiry**: 24 hours (configurable)
- **Cache Size**: Unlimited (monitor disk usage)

### Cache Management

```python
from xtrade_ai.utils.url_model_loader import URLModelLoader

url_loader = URLModelLoader(config)

# Get cache information
cache_info = url_loader.get_cache_info()
print(f"Cache size: {cache_info['total_size_mb']:.2f} MB")
print(f"Files: {cache_info['files']}")

# Clear cache
url_loader.clear_cache()
```

## Error Handling

The URL model loading system includes comprehensive error handling:

### Network Errors
- Automatic retries with exponential backoff
- Configurable timeout and retry limits
- Graceful fallback for failed downloads

### Authentication Errors
- Clear error messages for missing credentials
- Support for various authentication methods
- Environment variable configuration

### File Format Errors
- Validation of downloaded files
- Support for encrypted models
- Fallback to placeholder models on failure

## Examples

### Complete Example

```python
from xtrade_ai import XTradeAIFramework, XTradeAIConfig
import pandas as pd

# Configure framework
config = XTradeAIConfig()
config.persistence.url_timeout = 600  # 10 minutes
config.persistence.cache_dir = "./model_cache"

# Initialize framework
framework = XTradeAIFramework(config)

# Load model from various sources
model_urls = [
    "https://api.example.com/models/trading_model_v1.models",
    "s3://my-bucket/models/forex_model.models",
    "gs://ml-models/crypto_trader.models"
]

for url in model_urls:
    try:
        success = framework.load_model(url, critical=False)
        if success:
            print(f"✅ Loaded model from {url}")
        else:
            print(f"❌ Failed to load from {url}")
    except Exception as e:
        print(f"❌ Error loading from {url}: {e}")

# Make predictions
data = pd.read_csv("market_data.csv")
predictions = framework.predict(data.values)
print(f"Made {len(predictions)} predictions")
```

### Production Deployment

```python
# Production configuration
config = XTradeAIConfig()
config.persistence.url_timeout = 300
config.persistence.url_retries = 5
config.persistence.enable_cache = True
config.persistence.cache_expiry = 168  # 1 week

# Load production model
framework = XTradeAIFramework(config)
success = framework.load_model(
    "s3://production-models/trading_model_latest.models",
    password=os.getenv("MODEL_PASSWORD")
)

if success:
    # Start trading
    framework.start_trading()
else:
    raise RuntimeError("Failed to load production model")
```

## Best Practices

### Security
- Use HTTPS URLs for production models
- Store passwords in environment variables
- Regularly rotate access credentials
- Validate model checksums when possible

### Performance
- Enable caching for frequently used models
- Use appropriate chunk sizes for large models
- Monitor cache disk usage
- Set reasonable timeouts for your network

### Reliability
- Implement retry logic in your applications
- Use multiple model sources for redundancy
- Monitor download success rates
- Have fallback models available

### Monitoring
- Log model download attempts and failures
- Track cache hit rates
- Monitor download times
- Alert on authentication failures

## Troubleshooting

### Common Issues

**Authentication Errors:**
```
Error: S3 client not available. Install boto3 and configure AWS credentials.
```
Solution: Install required packages and configure credentials.

**Timeout Errors:**
```
Error: Failed to download from URL after 3 attempts
```
Solution: Increase timeout or check network connectivity.

**Cache Issues:**
```
Error: Failed to cache file
```
Solution: Check disk space and cache directory permissions.

**Encryption Errors:**
```
Error: No decryption key or password provided
```
Solution: Provide correct password for encrypted models.

### Debug Mode

Enable verbose logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or use CLI verbose mode
# xtrade-ai --verbose url load --url https://example.com/model.models
```

## Dependencies

The URL model loading feature requires these optional dependencies:

```bash
# For S3 support
pip install boto3

# For Google Cloud Storage support
pip install google-cloud-storage

# For Azure Blob Storage support
pip install azure-storage-blob

# For HTTP/HTTPS support (usually included)
pip install requests
```

## Migration Guide

### From Local Models

If you're migrating from local model loading:

```python
# Old way
framework.load_model("./models/trading_model.models")

# New way (still works)
framework.load_model("./models/trading_model.models")

# New way with URL
framework.load_model("https://example.com/models/trading_model.models")
```

### From Custom Download Scripts

Replace custom download scripts with the built-in URL loader:

```python
# Old way
import requests
response = requests.get("https://example.com/model.models")
with open("model.models", "wb") as f:
    f.write(response.content)
framework.load_model("model.models")

# New way
framework.load_model("https://example.com/model.models")
```

## Future Enhancements

Planned features for URL model loading:

- **Model Versioning**: Automatic version management
- **Delta Updates**: Download only changed model parts
- **CDN Support**: Optimized delivery from CDNs
- **Model Registry**: Centralized model management
- **A/B Testing**: Support for model variants
- **Rollback Support**: Automatic model rollback on issues

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review error logs with verbose mode
3. Verify network connectivity and credentials
4. Test with a simple HTTP URL first
5. Consult the framework documentation

The URL model loading feature is designed to be robust and production-ready, providing seamless model distribution across various environments and platforms.

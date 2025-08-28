# XTrade-AI Framework Troubleshooting Guide

## Table of Contents

- [Common Issues](#common-issues)
- [Installation Problems](#installation-problems)
- [Configuration Issues](#configuration-issues)
- [Training Problems](#training-problems)
- [Prediction Issues](#prediction-issues)
- [Performance Issues](#performance-issues)
- [Memory Issues](#memory-issues)
- [Docker Issues](#docker-issues)
- [FAQ](#faq)

## Common Issues

### Issue: Import Errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'xtrade_ai'
ImportError: cannot import name 'XTradeAIFramework'
```

**Solutions:**

1. **Check Installation:**
```bash
pip list | grep xtrade-ai
```

2. **Reinstall Package:**
```bash
pip uninstall xtrade-ai
pip install xtrade-ai
```

3. **Check Python Environment:**
```bash
python --version
which python
pip --version
```

4. **Install with Dependencies:**
```bash
pip install xtrade-ai[all]
```

### Issue: Dependency Conflicts

**Symptoms:**
```
ERROR: Cannot uninstall 'torch'. It is a distutils installed project
```

**Solutions:**

1. **Use Virtual Environment:**
```bash
python -m venv xtrade_env
source xtrade_env/bin/activate  # Linux/Mac
# or
xtrade_env\Scripts\activate  # Windows
pip install xtrade-ai
```

2. **Force Reinstall:**
```bash
pip install --force-reinstall xtrade-ai
```

3. **Use Conda:**
```bash
conda create -n xtrade_env python=3.8
conda activate xtrade_env
pip install xtrade-ai
```

## Installation Problems

### Issue: Build Failures

**Symptoms:**
```
error: Microsoft Visual C++ 14.0 is required
```

**Solutions:**

1. **Install Visual C++ Build Tools (Windows):**
   - Download Visual Studio Build Tools
   - Install C++ build tools

2. **Use Pre-built Wheels:**
```bash
pip install --only-binary=all xtrade-ai
```

3. **Install System Dependencies (Linux):**
```bash
sudo apt-get update
sudo apt-get install build-essential python3-dev
```

### Issue: GPU Support

**Symptoms:**
```
CUDA not available
```

**Solutions:**

1. **Check CUDA Installation:**
```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
```

2. **Install CUDA Version:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

3. **Use CPU Only:**
```python
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
```

## Configuration Issues

### Issue: Invalid Configuration

**Symptoms:**
```
ValueError: Invalid configuration parameter
```

**Solutions:**

1. **Validate Configuration:**
```python
from xtrade_ai import XTradeAIConfig

config = XTradeAIConfig()
print(config.to_dict())
```

2. **Check Configuration File:**
```python
import yaml

with open('config.yaml', 'r') as f:
    config_data = yaml.safe_load(f)
    print(config_data)
```

3. **Use Default Configuration:**
```python
config = XTradeAIConfig()  # Use defaults
config.model.baseline_algorithm = "PPO"  # Set required field
```

### Issue: Missing Required Parameters

**Symptoms:**
```
ValueError: baseline_algorithm is required
```

**Solutions:**

1. **Set Required Parameters:**
```python
config = XTradeAIConfig()
config.model.baseline_algorithm = "PPO"  # Required
config.trading.initial_balance = 10000.0  # Required
```

2. **Check Configuration Schema:**
```python
# Required fields
required_fields = [
    'model.baseline_algorithm',
    'trading.initial_balance',
    'data.feature_columns'
]

for field in required_fields:
    if not hasattr(config, field):
        print(f"Missing required field: {field}")
```

## Training Problems

### Issue: Training Not Converging

**Symptoms:**
- Loss not decreasing
- Accuracy stuck at low values
- Model not learning

**Solutions:**

1. **Check Data Quality:**
```python
# Validate data
print(f"Data shape: {data.shape}")
print(f"Missing values: {data.isnull().sum().sum()}")
print(f"Data types: {data.dtypes}")
```

2. **Adjust Learning Rate:**
```python
config.model.learning_rate = 1e-4  # Try lower learning rate
# or
config.model.learning_rate = 1e-3  # Try higher learning rate
```

3. **Increase Training Time:**
```python
results = framework.train(data, epochs=500)  # More epochs
```

4. **Check Data Preprocessing:**
```python
from xtrade_ai import DataPreprocessor

preprocessor = DataPreprocessor(config)
processed_data = preprocessor.preprocess(data)
print(f"Processed data shape: {processed_data.shape}")
```

### Issue: Out of Memory During Training

**Symptoms:**
```
RuntimeError: CUDA out of memory
```

**Solutions:**

1. **Reduce Batch Size:**
```python
config.model.batch_size = 32  # Reduce from 64
```

2. **Reduce Data Size:**
```python
# Use smaller dataset for training
training_data = data.head(1000)  # Use first 1000 rows
```

3. **Enable Memory Optimization:**
```python
config.performance.enable_memory_optimization = True
config.performance.max_memory_usage = 0.8
```

4. **Use CPU Training:**
```python
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
```

### Issue: Model Not Saving

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied
```

**Solutions:**

1. **Check File Permissions:**
```bash
ls -la models/
chmod 755 models/
```

2. **Use Absolute Path:**
```python
import os
model_path = os.path.abspath('models/trained_model.pkl')
framework.save_model(model_path)
```

3. **Create Directory:**
```python
import os
os.makedirs('models', exist_ok=True)
framework.save_model('models/model.pkl')
```

## Prediction Issues

### Issue: Prediction Errors

**Symptoms:**
```
ValueError: Input data has wrong shape
```

**Solutions:**

1. **Check Input Data Format:**
```python
print(f"Input data shape: {data.shape}")
print(f"Required columns: {config.data.feature_columns}")
print(f"Available columns: {list(data.columns)}")
```

2. **Validate Data:**
```python
# Ensure required columns exist
missing_columns = set(config.data.feature_columns) - set(data.columns)
if missing_columns:
    print(f"Missing columns: {missing_columns}")
```

3. **Preprocess Data:**
```python
from xtrade_ai import DataPreprocessor

preprocessor = DataPreprocessor(config)
processed_data = preprocessor.preprocess(data)
prediction = framework.predict(processed_data)
```

### Issue: Model Not Loaded

**Symptoms:**
```
AttributeError: 'NoneType' object has no attribute 'predict'
```

**Solutions:**

1. **Check Model Loading:**
```python
framework = XTradeAIFramework.load_model('model.pkl')
if framework is None:
    print("Model loading failed")
```

2. **Verify Model File:**
```python
import os
if os.path.exists('model.pkl'):
    print("Model file exists")
    print(f"File size: {os.path.getsize('model.pkl')} bytes")
else:
    print("Model file not found")
```

3. **Recreate Framework:**
```python
config = XTradeAIConfig()
config.model.baseline_algorithm = "PPO"
framework = XTradeAIFramework(config)
framework.load_model('model.pkl')
```

## Performance Issues

### Issue: Slow Training

**Symptoms:**
- Training taking too long
- Low GPU utilization

**Solutions:**

1. **Enable GPU Acceleration:**
```python
config.performance.enable_gpu = True
config.performance.gpu_memory_fraction = 0.8
```

2. **Use Parallel Processing:**
```python
config.performance.enable_parallel = True
config.performance.num_workers = 4
```

3. **Optimize Data Loading:**
```python
# Use smaller data types
data = data.astype('float32')
```

4. **Profile Performance:**
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
framework.train(data, epochs=10)
profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

### Issue: Slow Predictions

**Symptoms:**
- Predictions taking too long
- High latency

**Solutions:**

1. **Use Batch Predictions:**
```python
predictions = framework.predict_batch(data_batch)
```

2. **Enable Caching:**
```python
config.performance.enable_caching = True
config.performance.cache_ttl = 3600
```

3. **Optimize Model:**
```python
# Use smaller model
config.model.hidden_dim = 64  # Reduce from 128
```

4. **Profile Prediction:**
```python
import time

start_time = time.time()
prediction = framework.predict(data)
end_time = time.time()

print(f"Prediction time: {end_time - start_time:.4f} seconds")
```

## Memory Issues

### Issue: High Memory Usage

**Symptoms:**
- System running out of memory
- Slow performance

**Solutions:**

1. **Monitor Memory Usage:**
```python
import psutil

memory = psutil.virtual_memory()
print(f"Memory usage: {memory.percent}%")
print(f"Available memory: {memory.available / 1024**3:.2f} GB")
```

2. **Enable Memory Cleanup:**
```python
config.performance.enable_memory_cleanup = True
config.performance.cleanup_frequency = 100
```

3. **Reduce Data Size:**
```python
# Use data sampling
data = data.sample(n=1000, random_state=42)
```

4. **Use Memory-Efficient Training:**
```python
framework.train_memory_efficient(data, epochs=100)
```

### Issue: Memory Leaks

**Symptoms:**
- Memory usage increasing over time
- System becoming unresponsive

**Solutions:**

1. **Force Garbage Collection:**
```python
import gc

gc.collect()
```

2. **Monitor Object References:**
```python
import sys

def get_object_size(obj):
    return sys.getsizeof(obj)

print(f"Framework size: {get_object_size(framework)} bytes")
```

3. **Use Context Managers:**
```python
with framework.training_context():
    results = framework.train(data, epochs=100)
```

## Docker Issues

### Issue: Docker Build Fails

**Symptoms:**
```
ERROR: failed to build: error building at step
```

**Solutions:**

1. **Check Dockerfile:**
```bash
docker build -t xtrade-ai . --no-cache
```

2. **Increase Build Resources:**
```bash
docker build --memory=4g --cpus=2 -t xtrade-ai .
```

3. **Use Multi-stage Build:**
```dockerfile
# Use multi-stage build to reduce image size
FROM python:3.11-slim as builder
# ... build stage

FROM python:3.11-slim
# ... production stage
```

### Issue: Container Not Starting

**Symptoms:**
```
Error response from daemon: OCI runtime create failed
```

**Solutions:**

1. **Check Container Logs:**
```bash
docker logs xtrade-ai-container
```

2. **Check Resource Limits:**
```bash
docker run --memory=2g --cpus=1 xtrade-ai:latest
```

3. **Check Port Conflicts:**
```bash
docker run -p 8000:8000 xtrade-ai:latest
```

### Issue: Volume Mounting

**Symptoms:**
```
Permission denied when accessing mounted volume
```

**Solutions:**

1. **Check Volume Permissions:**
```bash
chmod 755 ./data
chmod 755 ./models
```

2. **Use Named Volumes:**
```yaml
# docker-compose.yml
volumes:
  - xtrade_data:/app/data
  - xtrade_models:/app/models
```

3. **Set User Permissions:**
```dockerfile
USER xtrade
```

## FAQ

### Q: What are the system requirements?

**A:** 
- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- 2GB disk space
- GPU with CUDA support (optional but recommended)

### Q: How do I choose the right algorithm?

**A:**
- **PPO**: Good for continuous action spaces, stable training
- **DQN**: Good for discrete action spaces, sample efficient
- **A2C**: Good for parallel environments, faster training
- **XGBoost**: Good for tabular data, interpretable

### Q: How much data do I need for training?

**A:**
- Minimum: 1,000 data points
- Recommended: 10,000+ data points
- More data generally leads to better performance

### Q: How do I interpret the results?

**A:**
- **Total Return**: Overall profit/loss percentage
- **Sharpe Ratio**: Risk-adjusted returns (higher is better)
- **Max Drawdown**: Largest peak-to-trough decline
- **Win Rate**: Percentage of profitable trades

### Q: Can I use my own data?

**A:** Yes, as long as your data has the required OHLCV columns:
- open, high, low, close, volume
- timestamp index or column

### Q: How do I deploy to production?

**A:**
1. Train model in development
2. Save model to file
3. Deploy using Docker or direct installation
4. Set up monitoring and logging
5. Start with small amounts

### Q: Is this framework suitable for live trading?

**A:** The framework is designed for educational and research purposes. For live trading:
- Test thoroughly in simulation
- Start with small amounts
- Monitor performance closely
- Have proper risk management

### Q: How do I contribute to the project?

**A:**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Q: Where can I get help?

**A:**
- Check this troubleshooting guide
- Review the documentation
- Search existing issues
- Create a new issue with details
- Contact support: anasamu7@gmail.com

---

This troubleshooting guide covers the most common issues you might encounter. If you don't find your issue here, please check the documentation or create an issue with detailed information about your problem.

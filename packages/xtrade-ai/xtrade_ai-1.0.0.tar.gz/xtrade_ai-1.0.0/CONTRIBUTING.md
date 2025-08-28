# Contributing to XTrade-AI Framework

Thank you for your interest in contributing to the XTrade-AI Framework! This document provides guidelines and information for contributors.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Feature Requests](#feature-requests)
- [Code of Conduct](#code-of-conduct)

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- pip or conda
- Basic knowledge of Python, machine learning, and algorithmic trading

### Fork and Clone

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
```bash
git clone https://github.com/YOUR_USERNAME/xtrade-ai-framework.git
cd xtrade-ai-framework
```

3. **Add upstream remote**:
```bash
git remote add upstream https://github.com/anasamu/xtrade-ai-framework.git
```

4. **Create a development branch**:
```bash
git checkout -b feature/your-feature-name
```

## Development Setup

### Environment Setup

1. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

2. **Install development dependencies**:
```bash
pip install -e ".[dev]"
```

3. **Install pre-commit hooks**:
```bash
pre-commit install
```

### Project Structure

```
xtrade_ai/
├── __init__.py              # Main package initialization
├── xtrade_ai_framework.py   # Main framework class
├── config.py                # Configuration management
├── cli.py                   # Command-line interface
├── data_structures.py       # Data structures and types
├── data_preprocessor.py     # Data preprocessing
├── base_environment.py      # Base trading environment
├── attention_mechanism.py   # Attention mechanisms
├── policy_networks.py       # Policy networks
├── modules/                 # Trading modules
│   ├── __init__.py
│   ├── action_selector.py
│   ├── baseline3_integration.py
│   ├── risk_management.py
│   └── ...
└── utils/                   # Utility modules
    ├── __init__.py
    ├── logger.py
    ├── error_handler.py
    └── ...
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=xtrade_ai

# Run specific test file
pytest test/test_basic_imports.py

# Run tests in parallel
pytest -n auto
```

### Code Quality Checks

```bash
# Run linting
flake8 xtrade_ai/

# Run type checking
mypy xtrade_ai/

# Run formatting
black xtrade_ai/
isort xtrade_ai/

# Run all quality checks
pre-commit run --all-files
```

## Code Style

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- **Line length**: 88 characters (Black default)
- **Import sorting**: Use `isort`
- **String formatting**: Use f-strings (Python 3.6+)
- **Type hints**: Use type hints for all functions and methods

### Code Formatting

We use [Black](https://black.readthedocs.io/) for code formatting:

```bash
# Format code
black xtrade_ai/

# Check formatting
black --check xtrade_ai/
```

### Import Sorting

We use [isort](https://pycqa.github.io/isort/) for import sorting:

```bash
# Sort imports
isort xtrade_ai/

# Check import sorting
isort --check-only xtrade_ai/
```

### Type Hints

All functions and methods should have type hints:

```python
from typing import Dict, List, Optional, Union
import pandas as pd
import numpy as np

def process_data(
    data: pd.DataFrame,
    config: Optional[Dict[str, any]] = None
) -> pd.DataFrame:
    """Process input data according to configuration.
    
    Args:
        data: Input DataFrame with OHLCV data
        config: Optional configuration dictionary
        
    Returns:
        Processed DataFrame
    """
    # Implementation here
    return processed_data
```

### Docstrings

Use Google-style docstrings:

```python
def calculate_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate technical indicators for the given data.
    
    Args:
        data: DataFrame with OHLCV columns
        
    Returns:
        DataFrame with additional indicator columns
        
    Raises:
        ValueError: If required columns are missing
        
    Example:
        >>> data = pd.DataFrame({'close': [100, 101, 102]})
        >>> result = calculate_indicators(data)
        >>> print(result.columns)
        ['close', 'sma_20', 'rsi_14']
    """
    # Implementation here
    return data_with_indicators
```

## Testing

### Test Structure

Tests should be organized as follows:

```
test/
├── __init__.py
├── test_basic_imports.py      # Basic import tests
├── test_config.py            # Configuration tests
├── test_data_preprocessor.py # Data preprocessing tests
├── test_framework.py         # Main framework tests
├── test_modules/             # Module-specific tests
│   ├── test_action_selector.py
│   ├── test_risk_management.py
│   └── ...
└── test_utils/               # Utility tests
    ├── test_logger.py
    ├── test_error_handler.py
    └── ...
```

### Writing Tests

Use pytest for testing:

```python
import pytest
import pandas as pd
from xtrade_ai import XTradeAIFramework, XTradeAIConfig

class TestXTradeAIFramework:
    """Test cases for XTradeAIFramework."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        return pd.DataFrame({
            'timestamp': pd.date_range('2023-01-01', periods=100, freq='1H'),
            'open': [100.0] * 100,
            'high': [101.0] * 100,
            'low': [99.0] * 100,
            'close': [100.5] * 100,
            'volume': [1000] * 100
        })
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        config = XTradeAIConfig()
        config.model.baseline_algorithm = "PPO"
        config.trading.initial_balance = 10000.0
        return config
    
    def test_framework_initialization(self, config):
        """Test framework initialization."""
        framework = XTradeAIFramework(config)
        assert framework is not None
        assert framework.config == config
    
    def test_data_preprocessing(self, sample_data, config):
        """Test data preprocessing."""
        framework = XTradeAIFramework(config)
        processed_data = framework.preprocess_data(sample_data)
        assert len(processed_data) == len(sample_data)
        assert 'returns' in processed_data.columns
    
    def test_model_training(self, sample_data, config):
        """Test model training."""
        framework = XTradeAIFramework(config)
        results = framework.train(sample_data, epochs=5)
        assert 'final_loss' in results
        assert results['final_loss'] >= 0
    
    def test_prediction(self, sample_data, config):
        """Test prediction functionality."""
        framework = XTradeAIFramework(config)
        framework.train(sample_data, epochs=5)
        prediction = framework.predict(sample_data.tail(10))
        assert 'action' in prediction
        assert 'confidence' in prediction
```

### Test Coverage

Maintain high test coverage:

```bash
# Run tests with coverage
pytest --cov=xtrade_ai --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Integration Tests

Write integration tests for complex workflows:

```python
def test_end_to_end_workflow():
    """Test complete workflow from data to prediction."""
    # Setup
    config = XTradeAIConfig()
    config.model.baseline_algorithm = "PPO"
    
    # Create sample data
    data = create_sample_data(1000)
    
    # Initialize framework
    framework = XTradeAIFramework(config)
    
    # Train model
    results = framework.train(data, epochs=10)
    assert results['final_loss'] >= 0
    
    # Make prediction
    prediction = framework.predict(data.tail(50))
    assert 'action' in prediction
    
    # Save and load model
    framework.save_model('test_model.pkl')
    loaded_framework = XTradeAIFramework.load_model('test_model.pkl')
    assert loaded_framework is not None
    
    # Cleanup
    import os
    os.remove('test_model.pkl')
```

## Documentation

### Code Documentation

- **Docstrings**: All public functions and classes must have docstrings
- **Type hints**: Use type hints for all function parameters and return values
- **Examples**: Include usage examples in docstrings

### API Documentation

Update API documentation when adding new features:

```python
def new_feature(data: pd.DataFrame, param: str) -> Dict[str, Any]:
    """New feature description.
    
    This function implements a new feature for the framework.
    
    Args:
        data: Input data
        param: Parameter description
        
    Returns:
        Dictionary containing results
        
    Example:
        >>> result = new_feature(data, "example")
        >>> print(result['status'])
        'success'
    """
    # Implementation
    return {'status': 'success', 'data': processed_data}
```

### README Updates

Update the README.md file when adding new features:

- Add new features to the features list
- Update installation instructions if needed
- Add usage examples
- Update requirements if new dependencies are added

### Documentation Structure

```
docs/
├── README.md              # Main documentation
├── ARCHITECTURE.md        # Architecture documentation
├── API_REFERENCE.md       # API reference
├── USER_GUIDE.md          # User guide
├── EXAMPLES.md            # Code examples
├── DEPLOYMENT.md          # Deployment guide
└── TROUBLESHOOTING.md     # Troubleshooting guide
```

## Pull Request Process

### Before Submitting

1. **Ensure tests pass**:
```bash
pytest
```

2. **Run code quality checks**:
```bash
pre-commit run --all-files
```

3. **Update documentation** if needed

4. **Add tests** for new functionality

### Pull Request Guidelines

1. **Title**: Use clear, descriptive titles
   - Good: "Add XGBoost ensemble support"
   - Bad: "Fix bug"

2. **Description**: Provide detailed description including:
   - What the PR does
   - Why the changes are needed
   - How to test the changes
   - Any breaking changes

3. **Size**: Keep PRs focused and reasonably sized
   - Prefer multiple small PRs over one large PR
   - Each PR should address one feature or bug

4. **Commits**: Use clear commit messages
   - Good: "feat: add XGBoost ensemble support"
   - Bad: "fix stuff"

### Commit Message Format

Use conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

Examples:
```
feat(ensemble): add XGBoost ensemble support

fix(data): handle missing values in preprocessing

docs(api): update API documentation

test(framework): add integration tests
```

### Review Process

1. **Self-review**: Review your own code before submitting
2. **CI checks**: Ensure all CI checks pass
3. **Review feedback**: Address reviewer feedback promptly
4. **Merge**: Once approved, maintainers will merge

## Issue Reporting

### Bug Reports

When reporting bugs, include:

1. **Environment information**:
   - Python version
   - Operating system
   - Package versions

2. **Steps to reproduce**:
   - Clear, step-by-step instructions
   - Minimal code example

3. **Expected vs actual behavior**:
   - What you expected to happen
   - What actually happened

4. **Error messages**:
   - Full error traceback
   - Any relevant log output

Example bug report:

```
**Environment:**
- Python: 3.9.7
- OS: Ubuntu 20.04
- XTrade-AI: 1.0.0

**Steps to reproduce:**
1. Create configuration with invalid parameters
2. Initialize framework
3. Call train() method

**Expected behavior:**
Framework should validate configuration and raise clear error

**Actual behavior:**
Framework crashes with cryptic error message

**Error message:**
```
Traceback (most recent call last):
  File "test.py", line 10, in <module>
    framework.train(data)
AttributeError: 'NoneType' object has no attribute 'train'
```

**Code example:**
```python
from xtrade_ai import XTradeAIFramework, XTradeAIConfig

config = XTradeAIConfig()
config.model.baseline_algorithm = "INVALID"
framework = XTradeAIFramework(config)
framework.train(data)  # This fails
```
```

### Feature Requests

When requesting features, include:

1. **Problem description**: What problem does this solve?
2. **Proposed solution**: How should it work?
3. **Use cases**: Who would benefit from this?
4. **Implementation ideas**: Any thoughts on implementation?

Example feature request:

```
**Problem:**
Currently, the framework only supports basic technical indicators. Users need more advanced indicators for better trading strategies.

**Proposed solution:**
Add support for advanced indicators like:
- Ichimoku Cloud
- Parabolic SAR
- Williams %R
- Stochastic RSI

**Use cases:**
- Advanced trading strategies
- Technical analysis research
- Backtesting with more indicators

**Implementation ideas:**
- Create new module `advanced_indicators.py`
- Integrate with existing technical analysis module
- Add configuration options for indicator parameters
```

## Code of Conduct

### Our Standards

We are committed to providing a welcoming and inspiring community for all. We expect all contributors to:

- Be respectful and inclusive
- Use welcoming and inclusive language
- Be collaborative and constructive
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

The following behaviors are considered harassment and are unacceptable:

- The use of sexualized language or imagery
- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

### Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by contacting the project team at anasamu7@gmail.com.

## Getting Help

### Questions and Support

- **Documentation**: Check the documentation first
- **Issues**: Search existing issues for similar problems
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact anasamu7@gmail.com for direct support

### Development Resources

- **Architecture Guide**: See `docs/ARCHITECTURE.md`
- **API Reference**: See `docs/API_REFERENCE.md`
- **Examples**: See `docs/EXAMPLES.md`
- **Testing Guide**: See test files for examples

### Community Guidelines

- Be patient and respectful
- Help others learn and grow
- Share knowledge and experiences
- Provide constructive feedback
- Follow the code of conduct

---

Thank you for contributing to the XTrade-AI Framework! Your contributions help make this project better for everyone.

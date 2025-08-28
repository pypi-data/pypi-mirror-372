# XTrade-AI Framework Deployment Guide

This guide explains how to deploy the XTrade-AI Framework to PyPI.

## Prerequisites

1. **Python Environment**: Python 3.8 or higher
2. **Build Tools**: Install build tools
   ```bash
   pip install build twine
   ```
3. **PyPI Account**: Create accounts on [PyPI](https://pypi.org) and [TestPyPI](https://test.pypi.org)
4. **API Tokens**: Generate API tokens for both PyPI and TestPyPI

## Configuration

### 1. PyPI Configuration

Create a `.pypirc` file in your home directory:

```bash
# Linux/Mac
nano ~/.pypirc

# Windows
notepad %USERPROFILE%\.pypirc
```

Add the following content:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
```

### 2. Environment Variables (Optional)

You can also use environment variables:

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-api-token-here
export TWINE_REPOSITORY_URL=https://upload.pypi.org/legacy/
```

## Build and Deploy Process

### Method 1: Using Makefile (Recommended)

```bash
# Clean build artifacts
make clean

# Build the package
make build

# Check the package
make check

# Upload to TestPyPI (for testing)
make test

# Upload to PyPI (for production)
make deploy
```

### Method 2: Using Python Script

```bash
# Clean and build
python scripts/build_and_deploy.py build

# Check package
python scripts/build_and_deploy.py check

# Upload to TestPyPI
python scripts/build_and_deploy.py test

# Upload to PyPI
python scripts/build_and_deploy.py deploy
```

### Method 3: Manual Commands

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Build the package
python -m build

# Check the package
twine check dist/*

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

## Testing Before Deployment

### 1. Local Testing

```bash
# Install in development mode
pip install -e .

# Run tests
make test-all

# Run linting
make lint

# Run security checks
make security-check
```

### 2. TestPyPI Testing

```bash
# Upload to TestPyPI
make test

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ xtrade-ai

# Test the installation
python -c "import xtrade_ai; print(xtrade_ai.__version__)"
```

## Version Management

### 1. Update Version

The version is managed by `setuptools_scm`. To update the version:

```bash
# Create a new git tag
git tag v1.0.1
git push origin v1.0.1
```

### 2. Manual Version Override

If you need to override the version:

```bash
# Set environment variable
export SETUPTOOLS_SCM_PRETEND_VERSION=1.0.1

# Build with specific version
python -m build
```

## Quality Checks

Before deploying, run these quality checks:

```bash
# Code formatting
make format

# Linting
make lint

# Security checks
make security-check

# Unit tests
make test-unit

# Integration tests
make test-integration
```

## Troubleshooting

### Common Issues

1. **Authentication Error**
   ```bash
   # Check your .pypirc file
   cat ~/.pypirc
   
   # Test authentication
   twine check dist/*
   ```

2. **Package Already Exists**
   ```bash
   # Check existing versions
   pip index versions xtrade-ai
   
   # Update version and rebuild
   git tag v1.0.2
   make clean build
   ```

3. **Build Errors**
   ```bash
   # Check Python version
   python --version
   
   # Check dependencies
   pip install -r requirements/base.txt
   
   # Clean and rebuild
   make clean build
   ```

### Debug Commands

```bash
# Check package contents
tar -tzf dist/xtrade-ai-*.tar.gz

# Check wheel contents
unzip -l dist/xtrade_ai-*.whl

# Validate package
twine check dist/*

# Test installation
pip install dist/xtrade_ai-*.whl --force-reinstall
```

## Post-Deployment

### 1. Verify Installation

```bash
# Install from PyPI
pip install xtrade-ai

# Test import
python -c "import xtrade_ai; print(xtrade_ai.__version__)"

# Test CLI
xtrade-ai --help
```

### 2. Update Documentation

- Update PyPI project description if needed
- Update GitHub repository
- Update documentation links

### 3. Monitor

- Check PyPI download statistics
- Monitor for issues on GitHub
- Check user feedback

## Security Best Practices

1. **Use API Tokens**: Never use username/password
2. **Token Permissions**: Use tokens with minimal required permissions
3. **Secure Storage**: Store tokens securely
4. **Regular Rotation**: Rotate tokens regularly
5. **Audit Logs**: Monitor PyPI upload logs

## Automation

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to PyPI

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Deploy to PyPI
      run: twine upload dist/*
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
```

## Support

For deployment issues:

1. Check the [PyPI documentation](https://packaging.python.org/tutorials/packaging-projects/)
2. Review [TestPyPI documentation](https://test.pypi.org/help/)
3. Check GitHub issues for similar problems
4. Contact the maintainer: anasamu7@gmail.com

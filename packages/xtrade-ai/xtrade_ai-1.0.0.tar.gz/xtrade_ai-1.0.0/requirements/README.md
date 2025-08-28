# Requirements Directory

This directory contains all Python dependency files for the XTrade-AI framework.

## Files

### Core Dependencies
- `base.txt` - Core dependencies (renamed from requirements.txt)
- `minimal.txt` - Minimal dependencies for basic functionality

### Development Dependencies
- `dev.txt` - Development tools and testing dependencies
- `docs.txt` - Documentation generation dependencies

### Docker Dependencies
- `docker.txt` - Dependencies for Docker containers
- `docker-pypi.txt` - Dependencies for PyPI-based Docker builds

## Usage

### Installation

```bash
# Install core dependencies
pip install -r requirements/base.txt

# Install development dependencies
pip install -r requirements/dev.txt

# Install minimal dependencies (for lightweight deployments)
pip install -r requirements/minimal.txt
```

### Docker Usage

```dockerfile
# In Dockerfile
COPY requirements/minimal.txt requirements/base.txt ./
RUN pip install -r requirements/minimal.txt
```

### Development Setup

```bash
# Full development environment
pip install -r requirements/base.txt
pip install -r requirements/dev.txt
pip install -r requirements/docs.txt

# Install package in editable mode
pip install -e .
```

## Dependency Categories

### Core Dependencies (`base.txt`)
- **AI/ML**: torch, stable-baselines3, gymnasium, xgboost
- **Data Processing**: numpy, pandas, scikit-learn, scipy
- **Trading**: technical analysis libraries
- **API**: fastapi, uvicorn, pydantic
- **Database**: sqlalchemy, psycopg2-binary, redis
- **Utilities**: click, pyyaml, python-dotenv

### Development Dependencies (`dev.txt`)
- **Testing**: pytest, pytest-cov, pytest-mock
- **Code Quality**: black, flake8, mypy, isort
- **Security**: bandit, safety
- **Documentation**: sphinx, sphinx-rtd-theme

### Documentation Dependencies (`docs.txt`)
- **Sphinx**: sphinx, sphinx-rtd-theme
- **Markdown**: myst-parser
- **Build Tools**: setuptools, wheel

### Docker Dependencies
- **Minimal**: Essential dependencies for production
- **PyPI**: Dependencies for PyPI-based installations

## Version Management

All dependencies use version constraints to ensure compatibility:
- `>=` for minimum versions
- `<` for maximum versions (excluding breaking changes)
- `~=` for compatible releases

## Adding New Dependencies

1. Add to appropriate requirements file
2. Update version constraints if needed
3. Test installation in clean environment
4. Update documentation if necessary

## Troubleshooting

### Version Conflicts
```bash
# Check for conflicts
pip check

# Resolve conflicts
pip install --upgrade pip
pip install -r requirements/base.txt --force-reinstall
```

### Platform-Specific Issues
Some dependencies may have platform-specific requirements:
- `ta-lib` requires system installation on some platforms
- `torch` has different versions for CPU/GPU
- `psycopg2-binary` is preferred over `psycopg2`

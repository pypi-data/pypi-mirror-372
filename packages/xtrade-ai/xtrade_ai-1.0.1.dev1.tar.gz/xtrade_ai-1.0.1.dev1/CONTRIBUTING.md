# Contributing to XTrade-AI Framework

Thank you for your interest in contributing to XTrade-AI Framework! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Docker (for testing deployment)
- Make (optional, for using Makefile commands)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/anasamu/xtrade-ai-framework.git
   cd xtrade-ai-framework
   ```

2. **Install Dependencies**
   ```bash
   # Install in development mode
   pip install -e ".[dev]"
   
   # Install pre-commit hooks
   pre-commit install
   ```

3. **Verify Setup**
   ```bash
   # Run tests
   pytest
   
   # Check code quality
   make lint
   ```

## 📝 Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Write clear, documented code
- Add tests for new functionality
- Update documentation as needed
- Follow the coding standards below

### 3. Test Your Changes

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=xtrade_ai --cov-report=html

# Run specific test categories
pytest -m "unit"
pytest -m "integration"
```

### 4. Code Quality Checks

```bash
# Format code
black .
isort .

# Lint code
flake8
mypy .

# Security checks
bandit -r xtrade_ai/
safety check
```

### 5. Commit Your Changes

```bash
git add .
git commit -m "feat: add new feature description"
```

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

## 🎯 Coding Standards

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions small and focused (max 50 lines)
- Use meaningful variable and function names

### Code Formatting

We use automated tools for code formatting:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

### Documentation Standards

- Use Google-style docstrings
- Include examples in docstrings
- Update README.md for user-facing changes
- Add docstrings for all public APIs

### Testing Standards

- Write unit tests for all new functionality
- Aim for at least 80% code coverage
- Use descriptive test names
- Group related tests in classes
- Use fixtures for common setup

## 🧪 Testing Guidelines

### Test Structure

```
test/
├── test_framework.py      # Framework tests
├── test_modules.py        # Module tests
├── test_utils.py          # Utility tests
├── test_integration.py    # Integration tests
└── conftest.py           # Test configuration
```

### Writing Tests

```python
import pytest
from xtrade_ai import XTradeAIFramework

class TestXTradeAIFramework:
    """Test cases for XTradeAIFramework."""
    
    def test_initialization(self):
        """Test framework initialization."""
        framework = XTradeAIFramework()
        assert framework is not None
        assert hasattr(framework, 'config')
    
    def test_training(self):
        """Test model training."""
        framework = XTradeAIFramework()
        # Add test implementation
        pass
```

### Test Categories

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test module interactions
- **Performance Tests**: Test performance characteristics
- **Security Tests**: Test security vulnerabilities

## 📚 Documentation

### Code Documentation

- Add docstrings to all public functions and classes
- Include type hints
- Provide usage examples
- Document exceptions and edge cases

### User Documentation

- Update README.md for user-facing changes
- Add examples and tutorials
- Document configuration options
- Provide troubleshooting guides

### API Documentation

- Document all public APIs
- Include request/response examples
- Document error codes and messages
- Provide SDK examples

## 🔒 Security Guidelines

### Security Best Practices

- Never commit sensitive data (API keys, passwords)
- Use environment variables for configuration
- Validate all user inputs
- Follow OWASP security guidelines
- Report security vulnerabilities privately

### Security Testing

```bash
# Run security checks
bandit -r xtrade_ai/
safety check
```

## 🚀 Release Process

### Version Management

We use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Code quality checks pass
- [ ] Documentation is updated
- [ ] Version is updated in `pyproject.toml`
- [ ] CHANGELOG.md is updated
- [ ] Release notes are prepared

### Creating a Release

```bash
# Build package
make build

# Test installation
make test-install

# Publish to PyPI
make publish
```

## 🤝 Pull Request Guidelines

### PR Requirements

- [ ] All tests pass
- [ ] Code quality checks pass
- [ ] Documentation is updated
- [ ] Commit messages follow conventional commits
- [ ] PR description is clear and complete

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

## 🐛 Bug Reports

### Bug Report Template

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., Ubuntu 20.04]
- Python: [e.g., 3.10.0]
- XTrade-AI: [e.g., 1.0.0]

## Additional Information
Screenshots, logs, etc.
```

## 💡 Feature Requests

### Feature Request Template

```markdown
## Feature Description
Clear description of the feature

## Use Case
Why this feature is needed

## Proposed Solution
How the feature should work

## Alternatives Considered
Other approaches considered

## Additional Information
Mockups, examples, etc.
```

## 📞 Getting Help

### Communication Channels

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: anasamu7@gmail.com

### Before Asking for Help

1. Check existing issues and discussions
2. Read the documentation
3. Try to reproduce the issue
4. Provide detailed information

## 🙏 Recognition

Contributors will be recognized in:

- GitHub contributors list
- Release notes
- Documentation acknowledgments
- Project README

## 📄 License

By contributing to XTrade-AI Framework, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to XTrade-AI Framework! 🚀

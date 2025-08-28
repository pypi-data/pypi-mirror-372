# ReadTheDocs Troubleshooting Guide

This guide helps resolve common issues with ReadTheDocs documentation builds.

## Common Issues and Solutions

### 1. Build Fails with "Unknown problem"

**Symptoms:**
- Build fails with generic "Unknown problem" error
- No specific error message provided

**Solutions:**
1. Check Python version compatibility
2. Verify all dependencies are available
3. Test build locally using `test_rtd_build.py`

### 2. Import Errors

**Symptoms:**
- `ImportError` for xtrade_ai or other modules
- Module not found errors

**Solutions:**
1. Ensure `requirements-docs.txt` includes all necessary dependencies
2. Check that the module is properly installed
3. Verify the `sys.path` configuration in `conf.py`

### 3. Sphinx Configuration Issues

**Symptoms:**
- Sphinx build fails
- Configuration errors

**Solutions:**
1. Test configuration locally: `python -c "from docs.conf import *; print('Config OK')"`
2. Check for syntax errors in `conf.py`
3. Verify all extensions are available

### 4. Python Version Issues

**Symptoms:**
- Build fails with Python version errors
- Incompatible dependencies

**Solutions:**
1. Use Python 3.10 (specified in `readthedocs.yml`)
2. Update `requirements-docs.txt` with compatible versions
3. Test with the exact Python version used by ReadTheDocs

## Local Testing

### Test ReadTheDocs Environment Locally

```bash
# Run the test script
python test_rtd_build.py

# Test Sphinx configuration
python -c "from docs.conf import *; print('Configuration OK')"

# Test documentation build
cd docs
sphinx-build -b html . _build/html
```

### Environment Variables

The test script sets these environment variables to simulate ReadTheDocs:

```bash
READTHEDOCS=True
READTHEDOCS_VERSION=latest
READTHEDOCS_PROJECT=xtrade-ai
```

## Configuration Files

### readthedocs.yml
- Main configuration file for ReadTheDocs
- Specifies Python version, build settings, and requirements

### requirements-docs.txt
- Python dependencies for documentation build
- Should include Sphinx and related packages

### docs/conf.py
- Sphinx configuration file
- Handles ReadTheDocs environment detection
- Configures extensions and settings

## Debugging Steps

1. **Check ReadTheDocs logs** for specific error messages
2. **Test locally** using the provided test script
3. **Verify dependencies** are correctly specified
4. **Check Python version** compatibility
5. **Review Sphinx configuration** for errors

## Common Fixes

### Update Python Version
```yaml
# In readthedocs.yml
build:
  os: ubuntu-24.04
  tools:
    python: "3.10"  # Use stable version
```

### Add Missing Dependencies
```txt
# In requirements-docs.txt
sphinx>=4.0.0,<9.0.0
sphinx-rtd-theme>=1.0.0,<4.0.0
myst-parser>=0.18.0,<5.0.0
```

### Handle Import Errors
```python
# In docs/conf.py
on_rtd = os.environ.get('READTHEDOCS') == 'True'
if on_rtd:
    try:
        import xtrade_ai
    except ImportError:
        # Handle gracefully
        pass
```

## Getting Help

If issues persist:

1. Check the [ReadTheDocs documentation](https://docs.readthedocs.io/)
2. Review the [Sphinx documentation](https://www.sphinx-doc.org/)
3. Check the build logs in your ReadTheDocs project dashboard
4. Test the configuration locally using the provided tools

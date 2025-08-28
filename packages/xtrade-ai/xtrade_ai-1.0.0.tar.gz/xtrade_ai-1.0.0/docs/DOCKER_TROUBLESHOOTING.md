# Docker Build Troubleshooting Guide

## Common Docker Build Issues and Solutions

### Issue: "failed to solve: process did not complete successfully: exit code: 1"

This error typically occurs during the pip installation step in the Docker build process. Here are the most common causes and solutions:

#### 1. Dependency Conflicts

**Problem**: Conflicting package versions or incompatible dependencies.

**Solutions**:
- Use `requirements-docker.txt` instead of `requirements.txt` for Docker builds
- Install dependencies in the correct order (numpy, scikit-learn, then others)
- Use `--prefer-binary` flag for packages like scikit-learn

#### 2. setuptools_scm Version Issues

**Problem**: setuptools_scm cannot determine the package version during Docker build.

**Solutions**:
- Set `SETUPTOOLS_SCM_PRETEND_VERSION=1.0.0` environment variable
- Ensure `xtrade_ai/_version.py` exists before package installation
- Use fallback installation strategies

#### 3. Memory Issues During Build

**Problem**: Insufficient memory during compilation of packages like numpy, scikit-learn.

**Solutions**:
- Increase Docker build memory limit
- Use pre-compiled binary packages when possible
- Install packages one by one to identify problematic ones

#### 4. System Dependencies Missing

**Problem**: Missing system-level dependencies required for Python packages.

**Solutions**:
- Ensure `build-essential` is installed
- Add required system packages to Dockerfile
- Use appropriate base image (python:3.11-slim)

## Dockerfile Options

### 1. Dockerfile.simple (Recommended)
- Uses minimal dependencies
- Better error handling
- Multiple fallback installation strategies
- Faster build times

### 2. Dockerfile.robust
- Full feature set
- More comprehensive dependencies
- May take longer to build
- Higher chance of dependency conflicts

### 3. Dockerfile (Standard)
- Balanced approach
- Good for development
- May need adjustments for production

## Build Commands

### Local Testing
```bash
# Test with simple Dockerfile
docker build -f Dockerfile.simple -t xtrade-ai:test .

# Test with robust Dockerfile
docker build -f Dockerfile.robust -t xtrade-ai:robust .

# Test with standard Dockerfile
docker build -f Dockerfile -t xtrade-ai:standard .
```

### Debug Build Issues
```bash
# Build with verbose output
docker build --progress=plain --no-cache -f Dockerfile.simple -t xtrade-ai:debug .

# Build specific stage
docker build --target build-stage -f Dockerfile.simple -t xtrade-ai:stage .
```

## Environment Variables

### Required for Build
- `SETUPTOOLS_SCM_PRETEND_VERSION=1.0.0` - Prevents version resolution issues
- `PYTHONUNBUFFERED=1` - Ensures Python output is not buffered
- `DEBIAN_FRONTEND=noninteractive` - Prevents interactive prompts

### Optional for Build
- `PIP_NO_CACHE_DIR=1` - Disables pip caching
- `PYTHONDONTWRITEBYTECODE=1` - Prevents .pyc file creation

## Common Fixes

### 1. Fix Version Issues
```dockerfile
# Add to Dockerfile
ENV SETUPTOOLS_SCM_PRETEND_VERSION=1.0.0
RUN echo "__version__ = '1.0.0'" > xtrade_ai/_version.py
```

### 2. Fix Dependency Order
```dockerfile
# Install in correct order
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir cython numpy && \
    pip install --no-cache-dir --prefer-binary scikit-learn && \
    pip install --no-cache-dir -r requirements-docker.txt
```

### 3. Fix Installation Issues
```dockerfile
# Multiple fallback strategies
RUN set -e; \
    pip install --no-cache-dir -e . || \
    pip install --no-cache-dir . || \
    SETUPTOOLS_SCM_PRETEND_VERSION=1.0.0 pip install --no-cache-dir .
```

## Monitoring and Debugging

### Check Build Logs
```bash
# Save build logs to file
docker build -f Dockerfile.simple -t xtrade-ai:test . 2>&1 | tee build.log

# Analyze specific step
docker build --progress=plain -f Dockerfile.simple -t xtrade-ai:test . | grep -A 10 -B 10 "ERROR"
```

### Test Package Installation
```bash
# Run container and test imports
docker run --rm -it xtrade-ai:test python -c "import xtrade_ai; print('Success')"

# Check installed packages
docker run --rm -it xtrade-ai:test pip list
```

## CI/CD Considerations

### GitHub Actions
- Use `continue-on-error: true` for non-critical steps
- Cache Docker layers for faster builds
- Use appropriate runners (ubuntu-latest recommended)
- Set up proper secrets for Docker Hub authentication

### Build Optimization
- Use multi-stage builds for smaller final images
- Leverage Docker layer caching
- Use .dockerignore to exclude unnecessary files
- Consider using BuildKit for better performance

## Support

If you continue to experience issues:

1. Check the build logs for specific error messages
2. Try building with the simple Dockerfile first
3. Ensure all system dependencies are installed
4. Verify Python package compatibility
5. Consider using a different base image if needed

## Quick Fix Checklist

- [ ] Use `Dockerfile.simple` for initial testing
- [ ] Set `SETUPTOOLS_SCM_PRETEND_VERSION=1.0.0`
- [ ] Use `requirements-docker.txt` instead of `requirements.txt`
- [ ] Install numpy and scikit-learn before other packages
- [ ] Use `--prefer-binary` for problematic packages
- [ ] Ensure `xtrade_ai/_version.py` exists
- [ ] Use multiple fallback installation strategies
- [ ] Test with `--no-cache` to avoid cached issues

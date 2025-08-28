# PyPI Deployment Troubleshooting Guide

This guide helps you resolve common PyPI deployment issues, particularly the "File already exists" error that occurs during automated deployments.

## Common Issues and Solutions

### 1. File Already Exists Error

**Error Message:**
```
ERROR HTTPError: 400 Bad Request from https://upload.pypi.org/legacy/
File already exists ('xtrade_ai-1.0.1.dev1-py3-none-any.whl', with blake2_256 hash '...')
```

**Cause:**
- Trying to upload the same version multiple times
- Development versions with the same build number
- Re-running workflows without version changes

**Solutions:**

#### A. For Development Versions (Recommended)
Development versions (e.g., `1.0.1.dev1`) can be uploaded multiple times. The workflow now uses `--skip-existing` flag:

```bash
# The workflow automatically handles this
twine upload --skip-existing dist/*
```

#### B. Increment Version Number
Update the version in your project:

```python
# In pyproject.toml
[project]
version = "1.0.1.dev2"  # Increment the dev number

# Or in setup.py
__version__ = "1.0.1.dev2"
```

#### C. Use Dynamic Versioning
Enable dynamic versioning with setuptools-scm:

```toml
# In pyproject.toml
[project]
dynamic = ["version"]

[tool.setuptools_scm]
write_to = "xtrade_ai/_version.py"
```

### 2. Version Management Best Practices

#### Development Workflow
```bash
# For development builds
version = "1.0.1.dev{N}"  # N increments with each build

# For release candidates
version = "1.0.1.rc1"

# For stable releases
version = "1.0.1"
```

#### Automated Version Increment
Add this to your workflow to automatically increment dev versions:

```yaml
- name: Increment dev version
  run: |
    # Get current version
    CURRENT_VERSION=$(python -c "import xtrade_ai; print(xtrade_ai.__version__)")
    echo "Current version: $CURRENT_VERSION"
    
    # Extract dev number and increment
    if [[ $CURRENT_VERSION =~ dev([0-9]+) ]]; then
      DEV_NUM=${BASH_REMATCH[1]}
      NEW_DEV_NUM=$((DEV_NUM + 1))
      NEW_VERSION="${CURRENT_VERSION%dev*}dev$NEW_DEV_NUM"
      echo "New version: $NEW_VERSION"
      
      # Update version in files
      sed -i "s/__version__ = \"$CURRENT_VERSION\"/__version__ = \"$NEW_VERSION\"/" xtrade_ai/_version.py
    fi
```

### 3. PyPI Credentials Issues

#### Missing API Token
**Error:** `PyPI API token not found`

**Solution:**
1. Go to [PyPI Account Settings](https://pypi.org/manage/account/)
2. Create an API token
3. Add to GitHub Secrets:
   - Name: `PYPI_API_TOKEN`
   - Value: `pypi-...` (your token)

#### Invalid Token
**Error:** `403 Forbidden`

**Solution:**
- Regenerate your PyPI API token
- Ensure the token has upload permissions
- Check token scope (should be for the specific project)

### 4. Package Validation Issues

#### Twine Check Failures
**Error:** `twine check failed`

**Solution:**
```bash
# Run twine check locally first
twine check dist/*

# Common issues:
# - Missing README.md
# - Invalid classifiers
# - Missing required metadata
```

#### Build Failures
**Error:** `build failed`

**Solution:**
```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Rebuild
python -m build --wheel --sdist
```

### 5. Workflow Configuration

#### Current Workflow Behavior
The updated workflow now:
- Uses `--skip-existing` flag to handle existing files gracefully
- Provides detailed feedback about upload status
- Continues execution even if some files already exist
- Shows version information for debugging

#### Manual Override
To force upload even if files exist:

```yaml
- name: Force PyPI Upload
  run: |
    # Remove existing files from PyPI (use with caution)
    # This requires special permissions and should be used carefully
    twine upload --force-replace dist/*
```

### 6. Development vs Release Workflow

#### Development Workflow
```yaml
# For development builds
- name: Build dev package
  run: |
    # Use development versioning
    python -m build --wheel --sdist
    # Upload with skip-existing
    twine upload --skip-existing dist/*
```

#### Release Workflow
```yaml
# For release builds
- name: Build release package
  run: |
    # Ensure version is not dev/rc
    python -c "import xtrade_ai; assert 'dev' not in xtrade_ai.__version__"
    python -m build --wheel --sdist
    # Upload without skip-existing for releases
    twine upload dist/*
```

### 7. Monitoring and Debugging

#### Check PyPI Status
```bash
# Check if package exists
pip search xtrade-ai  # (deprecated, use web interface)

# Check specific version
pip install xtrade-ai==1.0.1.dev1 --dry-run
```

#### Workflow Debugging
```yaml
- name: Debug Package Info
  run: |
    echo "Package files:"
    ls -la dist/
    echo ""
    echo "Package metadata:"
    python -c "import xtrade_ai; print(f'Version: {xtrade_ai.__version__}')"
    echo ""
    echo "Twine check:"
    twine check dist/* --verbose
```

### 8. Best Practices

#### Version Naming Convention
```
1.0.1.dev1    # Development version
1.0.1.rc1     # Release candidate
1.0.1         # Stable release
1.0.2.dev1    # Next development cycle
```

#### Automated Versioning
```python
# In _version.py
import os
from datetime import datetime

# Auto-increment dev version
def get_dev_version():
    base_version = "1.0.1"
    if os.getenv("GITHUB_RUN_NUMBER"):
        dev_num = int(os.getenv("GITHUB_RUN_NUMBER"))
        return f"{base_version}.dev{dev_num}"
    return f"{base_version}.dev1"

__version__ = get_dev_version()
```

#### Pre-upload Validation
```yaml
- name: Validate Package
  run: |
    # Check package structure
    python -c "import xtrade_ai; print('Package imports successfully')"
    
    # Validate metadata
    twine check dist/*
    
    # Test installation
    pip install dist/*.whl --force-reinstall
    python -c "import xtrade_ai; print(f'Installed version: {xtrade_ai.__version__}')"
```

## Quick Fixes

### Immediate Solutions

1. **For Development Versions:**
   - The workflow now handles this automatically
   - No action needed

2. **For Release Versions:**
   - Increment version number
   - Re-run workflow

3. **For Credentials:**
   - Add `PYPI_API_TOKEN` to GitHub Secrets
   - Ensure token has upload permissions

### Long-term Solutions

1. **Implement Dynamic Versioning:**
   - Use setuptools-scm for automatic versioning
   - Tie versions to git commits

2. **Separate Development and Release Workflows:**
   - Different triggers for dev vs release
   - Different versioning strategies

3. **Add Pre-upload Validation:**
   - Check version uniqueness
   - Validate package metadata
   - Test installation

## Support

If you continue to experience issues:

1. Check the workflow logs for detailed error messages
2. Verify PyPI credentials and permissions
3. Test package locally before uploading
4. Review PyPI's [file name reuse policy](https://pypi.org/help/#file-name-reuse)

For additional help, refer to:
- [PyPI Upload Documentation](https://packaging.python.org/tutorials/packaging-projects/#uploading-the-distribution-archives)
- [Twine Documentation](https://twine.readthedocs.io/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

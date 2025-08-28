# GitHub Actions Secrets

This document describes the required secrets for the XTrade-AI Framework GitHub Actions workflow.

## Required Secrets

### PyPI Deployment

**Name**: `PYPI_API_TOKEN`
**Description**: API token for uploading packages to PyPI
**Type**: Secret
**Required**: For PyPI deployment
**How to get**: 
1. Go to https://pypi.org/manage/account/token/
2. Create a new API token
3. Copy the token value

### TestPyPI Deployment

**Name**: `TESTPYPI_API_TOKEN`
**Description**: API token for uploading packages to TestPyPI
**Type**: Secret
**Required**: For TestPyPI deployment
**How to get**:
1. Go to https://test.pypi.org/manage/account/token/
2. Create a new API token
3. Copy the token value

### Docker Hub Deployment

**Name**: `DOCKER_USERNAME`
**Description**: Docker Hub username
**Type**: Secret
**Required**: For Docker deployment
**How to get**: Your Docker Hub username

**Name**: `DOCKER_PASSWORD`
**Description**: Docker Hub password or access token
**Type**: Secret
**Required**: For Docker deployment
**How to get**:
1. Go to https://hub.docker.com/settings/security
2. Create a new access token
3. Use the token as password

## Optional Secrets

### Codecov Integration

**Name**: `CODECOV_TOKEN`
**Description**: Codecov token for coverage reporting
**Type**: Secret
**Required**: For Codecov integration
**How to get**:
1. Go to https://codecov.io/gh/[username]/[repo]/settings
2. Copy the upload token

### Slack Notifications

**Name**: `SLACK_WEBHOOK_URL`
**Description**: Slack webhook URL for notifications
**Type**: Secret
**Required**: For Slack notifications
**How to get**:
1. Create a Slack app
2. Add incoming webhook integration
3. Copy the webhook URL

## How to Add Secrets

1. Go to your GitHub repository
2. Click on "Settings"
3. Click on "Secrets and variables" → "Actions"
4. Click "New repository secret"
5. Enter the secret name and value
6. Click "Add secret"

## Security Best Practices

1. **Use API tokens instead of passwords** for PyPI and Docker Hub
2. **Rotate tokens regularly** (every 90 days)
3. **Use minimal permissions** for tokens
4. **Never commit secrets** to the repository
5. **Use environment-specific secrets** when possible

## Environment Variables

The workflow also uses these environment variables:

- `PYTHON_VERSION`: Python version to use (default: 3.11)
- `PYPI_PACKAGE_NAME`: Package name (default: xtrade-ai)
- `DOCKER_IMAGE_NAME`: Docker image name (default: xtrade-ai)

These are defined in the workflow file and don't need to be set as secrets.

## Troubleshooting

### PyPI Upload Fails
- Check if `PYPI_API_TOKEN` is set correctly
- Verify the token has upload permissions
- Check if the package version already exists

### Docker Build Fails
- Verify `DOCKER_USERNAME` and `DOCKER_PASSWORD` are correct
- Check if the Docker Hub account has the required permissions
- Ensure the repository exists on Docker Hub

### TestPyPI Upload Fails
- Check if `TESTPYPI_API_TOKEN` is set correctly
- Verify the token has upload permissions
- TestPyPI allows multiple uploads of the same version

## Support

For issues with secrets or deployment:
1. Check the GitHub Actions logs
2. Verify all required secrets are set
3. Test the deployment locally first
4. Contact the maintainer: anasamu7@gmail.com

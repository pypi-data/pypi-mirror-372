# XTrade-AI API Guide

This guide provides comprehensive documentation for the XTrade-AI REST API, enabling remote access to trading functionality, model management, and monitoring.

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Overview

The XTrade-AI API is a RESTful service built with FastAPI that provides programmatic access to the XTrade-AI trading framework. It supports:

- **Model Management**: Load, list, and manage trading models
- **Trading Operations**: View positions, orders, and portfolio
- **Predictions**: Make trading predictions using loaded models
- **User Management**: Manage users and API keys
- **Monitoring**: Health checks and system status

## Authentication

The API uses Bearer token authentication with API keys.

### Creating API Keys

1. **Create a user** (if you don't have one):
```bash
xtrade-ai api create-user --username myuser --email myuser@example.com --password mypassword
```

2. **Create an API key**:
```bash
xtrade-ai api create-key --username myuser --password mypassword --key-name "My API Key"
```

3. **Use the API key** in your requests:
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8000/models
```

### API Key Management

- **List your API keys**:
```bash
xtrade-ai api list-keys --username myuser --password mypassword
```

- **Revoke an API key**:
```bash
xtrade-ai api revoke-key --username myuser --password mypassword --key-id KEY_ID
```

## Getting Started

### 1. Start the API Server

```bash
# Start API server
xtrade-ai start-api --host 0.0.0.0 --port 8000

# Or with Docker
docker-compose up -d
```

### 2. Test the API

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test with API key
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8000/models
```

### 3. Access Documentation

- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check

#### GET /health

Check API health and dependencies.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-01T00:00:00Z",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "framework": "healthy"
  }
}
```

### Model Management

#### GET /models

List all available models.

**Headers:**
- `Authorization: Bearer YOUR_API_KEY`

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "my_model",
    "type": "PPO",
    "version": "1.0.0",
    "status": "READY",
    "file_path": "/path/to/model",
    "url": "https://example.com/model.models",
    "is_encrypted": false,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

#### POST /models/load

Load a model from path or URL.

**Headers:**
- `Authorization: Bearer YOUR_API_KEY`

**Request Body:**
```json
{
  "path": "https://example.com/model.models",
  "model_name": "my_model",
  "password": "optional_password"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Model loaded successfully",
  "model_info": {
    "id": "uuid",
    "name": "my_model",
    "type": "PPO",
    "version": "1.0.0",
    "status": "READY"
  }
}
```

### Trading Operations

#### GET /positions

List all trading positions.

**Headers:**
- `Authorization: Bearer YOUR_API_KEY`

**Response:**
```json
[
  {
    "id": "uuid",
    "symbol": "BTCUSD",
    "side": "BUY",
    "quantity": 1.0,
    "entry_price": 50000.0,
    "current_price": 51000.0,
    "pnl": 1000.0,
    "stop_loss": 49000.0,
    "take_profit": 52000.0,
    "strategy_name": "my_strategy",
    "status": "OPEN",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### GET /orders

List all trading orders.

**Headers:**
- `Authorization: Bearer YOUR_API_KEY`

**Response:**
```json
[
  {
    "id": "uuid",
    "symbol": "BTCUSD",
    "order_type": "MARKET",
    "side": "BUY",
    "quantity": 1.0,
    "price": 50000.0,
    "status": "FILLED",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### GET /portfolio

Get current portfolio information.

**Headers:**
- `Authorization: Bearer YOUR_API_KEY`

**Response:**
```json
{
  "balance": 10000.0,
  "equity": 11000.0,
  "margin": 0.0,
  "free_margin": 11000.0,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Predictions

#### POST /predict

Make a prediction using a loaded model.

**Headers:**
- `Authorization: Bearer YOUR_API_KEY`

**Request Body:**
```json
{
  "symbol": "BTCUSD",
  "model_name": "my_model",
  "data": {
    "price": 50000.0,
    "volume": 1000.0,
    "indicators": {}
  }
}
```

**Response:**
```json
{
  "symbol": "BTCUSD",
  "prediction": 0.65,
  "confidence": 0.85,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### User Management (Admin Only)

#### GET /users

List all users (admin only).

**Headers:**
- `Authorization: Bearer YOUR_API_KEY`

**Response:**
```json
[
  {
    "id": "uuid",
    "username": "admin",
    "email": "admin@xtrade-ai.com",
    "is_active": true,
    "is_admin": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### GET /api-keys

List API keys for current user.

**Headers:**
- `Authorization: Bearer YOUR_API_KEY`

**Response:**
```json
[
  {
    "id": "uuid",
    "key_name": "My API Key",
    "permissions": ["*"],
    "is_active": true,
    "last_used": "2024-01-01T00:00:00Z",
    "created_at": "2024-01-01T00:00:00Z",
    "expires_at": null
  }
]
```

## Error Handling

The API returns standard HTTP status codes:

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Invalid or missing API key
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

**Error Response Format:**
```json
{
  "detail": "Error message description"
}
```

## Rate Limiting

The API implements rate limiting:

- **General API**: 10 requests per second
- **Login endpoints**: 1 request per second
- **Burst allowance**: 20 requests

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Request limit per window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Time when the rate limit resets

## Examples

### Python Client Example

```python
import requests

# API configuration
API_BASE_URL = "http://localhost:8000"
API_KEY = "your_api_key_here"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Health check
response = requests.get(f"{API_BASE_URL}/health")
print(f"API Status: {response.json()['status']}")

# Load model from URL
model_data = {
    "path": "https://example.com/model.models",
    "model_name": "my_model"
}
response = requests.post(f"{API_BASE_URL}/models/load", json=model_data, headers=headers)
print(f"Model loaded: {response.json()['success']}")

# Get portfolio
response = requests.get(f"{API_BASE_URL}/portfolio", headers=headers)
portfolio = response.json()
print(f"Balance: ${portfolio['balance']}")

# Make prediction
prediction_data = {
    "symbol": "BTCUSD",
    "model_name": "my_model",
    "data": {"price": 50000.0}
}
response = requests.post(f"{API_BASE_URL}/predict", json=prediction_data, headers=headers)
prediction = response.json()
print(f"Prediction: {prediction['prediction']} (confidence: {prediction['confidence']})")
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

// API configuration
const API_BASE_URL = 'http://localhost:8000';
const API_KEY = 'your_api_key_here';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json'
    }
});

// Health check
async function checkHealth() {
    try {
        const response = await api.get('/health');
        console.log(`API Status: ${response.data.status}`);
    } catch (error) {
        console.error('Health check failed:', error.message);
    }
}

// Load model
async function loadModel() {
    try {
        const modelData = {
            path: 'https://example.com/model.models',
            model_name: 'my_model'
        };
        const response = await api.post('/models/load', modelData);
        console.log(`Model loaded: ${response.data.success}`);
    } catch (error) {
        console.error('Model loading failed:', error.message);
    }
}

// Get portfolio
async function getPortfolio() {
    try {
        const response = await api.get('/portfolio');
        console.log(`Balance: $${response.data.balance}`);
    } catch (error) {
        console.error('Portfolio fetch failed:', error.message);
    }
}

// Run examples
checkHealth();
loadModel();
getPortfolio();
```

### cURL Examples

```bash
# Health check
curl http://localhost:8000/health

# Load model (with API key)
curl -X POST http://localhost:8000/models/load \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"path": "https://example.com/model.models", "model_name": "my_model"}'

# Get positions
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8000/positions

# Make prediction
curl -X POST http://localhost:8000/predict \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSD", "model_name": "my_model", "data": {"price": 50000.0}}'
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure the API server is running
   - Check if the port is correct (default: 8000)
   - Verify firewall settings

2. **401 Unauthorized**
   - Check if the API key is correct
   - Ensure the API key is not expired
   - Verify the Authorization header format

3. **500 Internal Server Error**
   - Check server logs for detailed error messages
   - Verify database connectivity
   - Ensure all required services are running

4. **Rate Limit Exceeded**
   - Reduce request frequency
   - Implement exponential backoff
   - Consider using multiple API keys

### Debug Mode

Enable verbose logging when starting the API server:

```bash
xtrade-ai start-api --verbose
```

### Logs

Check logs for detailed error information:

```bash
# Docker logs
docker-compose logs xtrade-ai

# Direct logs
tail -f logs/xtrade_ai.log
```

### Database Issues

If you encounter database-related errors:

1. **Check database connectivity**:
```bash
psql -h localhost -U xtrade_user -d xtrade_ai
```

2. **Verify database schema**:
```bash
psql -h localhost -U xtrade_user -d xtrade_ai -c "\dt"
```

3. **Reinitialize database**:
```bash
psql -h localhost -U xtrade_user -d xtrade_ai -f config/init.sql
```

## Security Considerations

1. **API Key Security**
   - Store API keys securely
   - Rotate keys regularly
   - Use environment variables for production

2. **Network Security**
   - Use HTTPS in production
   - Implement proper firewall rules
   - Consider VPN access for sensitive operations

3. **Access Control**
   - Use minimal required permissions
   - Implement IP whitelisting if needed
   - Monitor API usage

## Support

For API support and questions:

- **Documentation**: http://localhost:8000/docs
- **Issues**: GitHub repository issues
- **Email**: support@xtrade-ai.com

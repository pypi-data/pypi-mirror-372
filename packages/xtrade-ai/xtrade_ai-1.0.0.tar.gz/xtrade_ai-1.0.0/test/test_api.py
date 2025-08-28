"""
Test script for XTrade-AI API functionality.
"""

import requests
import json
import time
from typing import Dict, Any


def test_api_health(base_url: str = "http://localhost:8000") -> bool:
    """Test API health endpoint."""
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Health Check: {data['status']}")
            print(f"   Version: {data['version']}")
            print(f"   Services: {data['services']}")
            return True
        else:
            print(f"❌ API Health Check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Health Check error: {e}")
        return False


def test_api_root(base_url: str = "http://localhost:8000") -> bool:
    """Test API root endpoint."""
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Root: {data['message']}")
            print(f"   Version: {data['version']}")
            return True
        else:
            print(f"❌ API Root failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Root error: {e}")
        return False


def test_api_docs(base_url: str = "http://localhost:8000") -> bool:
    """Test API documentation endpoint."""
    try:
        response = requests.get(f"{base_url}/docs", timeout=10)
        if response.status_code == 200:
            print("✅ API Documentation accessible")
            return True
        else:
            print(f"❌ API Documentation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Documentation error: {e}")
        return False


def test_authenticated_endpoints(base_url: str = "http://localhost:8000", api_key: str = None) -> bool:
    """Test authenticated endpoints."""
    if not api_key:
        print("⚠️  No API key provided, skipping authenticated endpoint tests")
        return True
    
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Test models endpoint
    try:
        response = requests.get(f"{base_url}/models", headers=headers, timeout=10)
        if response.status_code == 200:
            models = response.json()
            print(f"✅ Models endpoint: {len(models)} models found")
        elif response.status_code == 401:
            print("❌ Models endpoint: Unauthorized (invalid API key)")
            return False
        else:
            print(f"❌ Models endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Models endpoint error: {e}")
        return False
    
    # Test portfolio endpoint
    try:
        response = requests.get(f"{base_url}/portfolio", headers=headers, timeout=10)
        if response.status_code == 200:
            portfolio = response.json()
            print(f"✅ Portfolio endpoint: Balance {portfolio['balance']}")
        elif response.status_code == 401:
            print("❌ Portfolio endpoint: Unauthorized (invalid API key)")
            return False
        else:
            print(f"❌ Portfolio endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Portfolio endpoint error: {e}")
        return False
    
    return True


def main():
    """Run all API tests."""
    print("🧪 Testing XTrade-AI API...")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test basic endpoints
    health_ok = test_api_health(base_url)
    root_ok = test_api_root(base_url)
    docs_ok = test_api_docs(base_url)
    
    # Test authenticated endpoints (optional)
    auth_ok = test_authenticated_endpoints(base_url)
    
    print("=" * 50)
    if all([health_ok, root_ok, docs_ok, auth_ok]):
        print("🎉 All API tests passed!")
        return True
    else:
        print("❌ Some API tests failed!")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

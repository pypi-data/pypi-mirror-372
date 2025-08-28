#!/usr/bin/env python3
"""
Example: URL-based Model Loading in XTrade-AI Framework

This example demonstrates how to load models from various URL sources including:
- HTTP/HTTPS URLs
- S3 URLs
- Google Cloud Storage URLs
- Azure Blob Storage URLs
- Local file paths

Usage:
    python url_model_loading_example.py
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from xtrade_ai import XTradeAIFramework, XTradeAIConfig
from xtrade_ai.utils.url_model_loader import URLModelLoader


def example_http_loading():
    """Example: Load model from HTTP/HTTPS URL."""
    print("=== HTTP/HTTPS Model Loading Example ===")
    
    # Example URLs (replace with actual URLs)
    example_urls = [
        "https://example.com/models/trading_model_v1.models",
        "http://localhost:8000/models/forex_model.models",
        "https://api.example.com/models/crypto_trader.models"
    ]
    
    config = XTradeAIConfig()
    framework = XTradeAIFramework(config)
    
    for url in example_urls:
        try:
            print(f"Loading model from: {url}")
            success = framework.load_model(url, critical=False)
            if success:
                print(f"✅ Successfully loaded model from {url}")
            else:
                print(f"❌ Failed to load model from {url}")
        except Exception as e:
            print(f"❌ Error loading from {url}: {e}")
    
    print()


def example_s3_loading():
    """Example: Load model from S3 URL."""
    print("=== S3 Model Loading Example ===")
    
    # Example S3 URLs (replace with actual URLs)
    s3_urls = [
        "s3://my-bucket/models/trading_model_v1.models",
        "s3://ai-models-bucket/forex/forex_model.models",
        "s3://ml-models/crypto/crypto_trader.models"
    ]
    
    config = XTradeAIConfig()
    framework = XTradeAIFramework(config)
    
    for url in s3_urls:
        try:
            print(f"Loading model from: {url}")
            success = framework.load_model(url, critical=False)
            if success:
                print(f"✅ Successfully loaded model from {url}")
            else:
                print(f"❌ Failed to load model from {url}")
        except Exception as e:
            print(f"❌ Error loading from {url}: {e}")
    
    print()


def example_cloud_storage_loading():
    """Example: Load model from Google Cloud Storage or Azure Blob Storage."""
    print("=== Cloud Storage Model Loading Example ===")
    
    # Example cloud storage URLs (replace with actual URLs)
    cloud_urls = [
        "gs://my-bucket/models/trading_model_v1.models",  # Google Cloud Storage
        "azure://myaccount.blob.core.windows.net/container/model.models"  # Azure Blob Storage
    ]
    
    config = XTradeAIConfig()
    framework = XTradeAIFramework(config)
    
    for url in cloud_urls:
        try:
            print(f"Loading model from: {url}")
            success = framework.load_model(url, critical=False)
            if success:
                print(f"✅ Successfully loaded model from {url}")
            else:
                print(f"❌ Failed to load model from {url}")
        except Exception as e:
            print(f"❌ Error loading from {url}: {e}")
    
    print()


def example_encrypted_model_loading():
    """Example: Load encrypted models with password."""
    print("=== Encrypted Model Loading Example ===")
    
    # Example encrypted model URL
    encrypted_url = "https://example.com/models/encrypted_trading_model.models"
    password = "my_secret_password"
    
    config = XTradeAIConfig()
    framework = XTradeAIFramework(config)
    
    try:
        print(f"Loading encrypted model from: {encrypted_url}")
        success = framework.load_model(encrypted_url, critical=False, password=password)
        if success:
            print(f"✅ Successfully loaded encrypted model from {encrypted_url}")
        else:
            print(f"❌ Failed to load encrypted model from {encrypted_url}")
    except Exception as e:
        print(f"❌ Error loading encrypted model: {e}")
    
    print()


def example_url_loader_direct():
    """Example: Use URLModelLoader directly for more control."""
    print("=== Direct URLModelLoader Example ===")
    
    config = XTradeAIConfig()
    url_loader = URLModelLoader(config)
    
    # Example URLs
    urls = [
        "https://example.com/models/model1.models",
        "s3://my-bucket/models/model2.models",
        "gs://my-bucket/models/model3.models"
    ]
    
    for url in urls:
        try:
            print(f"Downloading model from: {url}")
            downloaded_path = url_loader.load_model_from_url(url)
            print(f"✅ Model downloaded to: {downloaded_path}")
            
            # Get cache info
            cache_info = url_loader.get_cache_info()
            print(f"   Cache contains {cache_info['file_count']} files")
            
        except Exception as e:
            print(f"❌ Error downloading from {url}: {e}")
    
    print()


def example_cache_management():
    """Example: Cache management operations."""
    print("=== Cache Management Example ===")
    
    config = XTradeAIConfig()
    url_loader = URLModelLoader(config)
    
    # Get cache information
    cache_info = url_loader.get_cache_info()
    print("📁 Current Cache Information:")
    print(f"   Cache Directory: {cache_info['cache_dir']}")
    print(f"   File Count: {cache_info['file_count']}")
    print(f"   Total Size: {cache_info['total_size_mb']:.2f} MB")
    
    if cache_info['files']:
        print(f"   Cached Files: {', '.join(cache_info['files'])}")
    
    # Example: Clear cache (commented out for safety)
    # print("\nClearing cache...")
    # url_loader.clear_cache()
    # print("✅ Cache cleared")
    
    print()


def example_configuration():
    """Example: Configure URL loading settings."""
    print("=== Configuration Example ===")
    
    # Create custom configuration
    config = XTradeAIConfig()
    
    # Configure persistence settings
    config.persistence.url_timeout = 600  # 10 minutes
    config.persistence.url_retries = 5
    config.persistence.url_chunk_size = 16384  # 16KB chunks
    config.persistence.cache_dir = "./custom_cache"
    config.persistence.enable_cache = True
    config.persistence.cache_expiry = 48  # 48 hours
    
    print("🔧 URL Loading Configuration:")
    print(f"   Timeout: {config.persistence.url_timeout} seconds")
    print(f"   Retries: {config.persistence.url_retries}")
    print(f"   Chunk Size: {config.persistence.url_chunk_size} bytes")
    print(f"   Cache Directory: {config.persistence.cache_dir}")
    print(f"   Cache Enabled: {config.persistence.enable_cache}")
    print(f"   Cache Expiry: {config.persistence.cache_expiry} hours")
    
    # Initialize framework with custom config
    framework = XTradeAIFramework(config)
    
    print()


def main():
    """Run all URL model loading examples."""
    print("🚀 XTrade-AI URL Model Loading Examples")
    print("=" * 50)
    
    # Run examples
    example_http_loading()
    example_s3_loading()
    example_cloud_storage_loading()
    example_encrypted_model_loading()
    example_url_loader_direct()
    example_cache_management()
    example_configuration()
    
    print("✅ All examples completed!")
    print("\n📝 Notes:")
    print("   - Replace example URLs with actual model URLs")
    print("   - Configure cloud storage credentials as needed")
    print("   - Use appropriate passwords for encrypted models")
    print("   - Check cache settings for optimal performance")


if __name__ == "__main__":
    main()

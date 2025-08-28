#!/usr/bin/env python3
"""
Test URL Model Loading Functionality

This module tests the URL model loading capabilities of the XTrade-AI framework.
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import json

# Add the project root to the Python path
import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from xtrade_ai import XTradeAIFramework, XTradeAIConfig
from xtrade_ai.utils.url_model_loader import URLModelLoader


class TestURLModelLoading(unittest.TestCase):
    """Test URL model loading functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = XTradeAIConfig()
        self.framework = XTradeAIFramework(self.config)
        self.url_loader = URLModelLoader(self.config)
        
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.config.persistence.cache_dir = self.temp_dir
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_url_loader_initialization(self):
        """Test URLModelLoader initialization."""
        self.assertIsNotNone(self.url_loader)
        self.assertEqual(self.url_loader.config, self.config)
        self.assertTrue(Path(self.url_loader.cache_dir).exists())
    
    def test_parse_local_path(self):
        """Test parsing local file paths."""
        # Test local file path without scheme
        local_path = "/path/to/local/model.models"
        with self.assertRaises(FileNotFoundError):
            self.url_loader.load_model_from_url(local_path)
    
    def test_parse_file_scheme(self):
        """Test parsing file:// URLs."""
        # Test file:// scheme
        file_url = "file:///path/to/local/model.models"
        with self.assertRaises(FileNotFoundError):
            self.url_loader.load_model_from_url(file_url)
    
    def test_unsupported_scheme(self):
        """Test handling of unsupported URL schemes."""
        unsupported_url = "ftp://example.com/model.models"
        with self.assertRaises(ValueError):
            self.url_loader.load_model_from_url(unsupported_url)
    
    @patch('xtrade_ai.utils.url_model_loader.requests.get')
    def test_http_download_success(self, mock_get):
        """Test successful HTTP download."""
        # Mock successful HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'content-length': '1024'}
        mock_response.iter_content.return_value = [b'test' * 256]  # 1024 bytes
        mock_get.return_value = mock_response
        
        url = "https://example.com/model.models"
        result = self.url_loader.load_model_from_url(url)
        
        self.assertIsInstance(result, str)
        self.assertTrue(Path(result).exists())
        self.assertEqual(Path(result).suffix, '.models')
    
    @patch('xtrade_ai.utils.url_model_loader.requests.get')
    def test_http_download_failure(self, mock_get):
        """Test HTTP download failure."""
        # Mock failed HTTP response
        mock_get.side_effect = Exception("Network error")
        
        url = "https://example.com/model.models"
        with self.assertRaises(Exception):
            self.url_loader.load_model_from_url(url)
    
    @patch('xtrade_ai.utils.url_model_loader.boto3.client')
    def test_s3_download_success(self, mock_boto3_client):
        """Test successful S3 download."""
        # Mock S3 client
        mock_s3_client = MagicMock()
        mock_boto3_client.return_value = mock_s3_client
        
        url = "s3://my-bucket/model.models"
        result = self.url_loader.load_model_from_url(url)
        
        # Should call S3 download_file
        mock_s3_client.download_file.assert_called_once()
    
    @patch('xtrade_ai.utils.url_model_loader.boto3.client')
    def test_s3_download_no_credentials(self, mock_boto3_client):
        """Test S3 download without credentials."""
        # Mock S3 client failure
        from botocore.exceptions import NoCredentialsError
        mock_boto3_client.side_effect = NoCredentialsError()
        
        url = "s3://my-bucket/model.models"
        with self.assertRaises(Exception):
            self.url_loader.load_model_from_url(url)
    
    def test_cache_operations(self):
        """Test cache operations."""
        # Test cache info
        cache_info = self.url_loader.get_cache_info()
        self.assertIsInstance(cache_info, dict)
        self.assertIn('cache_dir', cache_info)
        self.assertIn('file_count', cache_info)
        self.assertIn('total_size_bytes', cache_info)
        self.assertIn('total_size_mb', cache_info)
        self.assertIn('files', cache_info)
        
        # Test cache clearing
        self.url_loader.clear_cache()
        cache_info_after = self.url_loader.get_cache_info()
        self.assertEqual(cache_info_after['file_count'], 0)
    
    def test_framework_url_loading(self):
        """Test framework URL model loading."""
        # Test with non-existent URL (should fail gracefully)
        success = self.framework.load_model("https://nonexistent.com/model.models", critical=False)
        self.assertFalse(success)
    
    def test_framework_local_path_loading(self):
        """Test framework local path loading (should still work)."""
        # Test with non-existent local path (should fail gracefully)
        success = self.framework.load_model("/nonexistent/path/model.models", critical=False)
        self.assertFalse(success)
    
    def test_persistence_config(self):
        """Test persistence configuration."""
        # Test default values
        self.assertEqual(self.config.persistence.url_timeout, 300)
        self.assertEqual(self.config.persistence.url_retries, 3)
        self.assertEqual(self.config.persistence.url_chunk_size, 8192)
        self.assertEqual(self.config.persistence.cache_dir, "./cache")
        self.assertTrue(self.config.persistence.enable_cache)
        self.assertEqual(self.config.persistence.cache_expiry, 24)
        
        # Test custom values
        self.config.persistence.url_timeout = 600
        self.config.persistence.url_retries = 5
        self.config.persistence.cache_dir = "./custom_cache"
        
        self.assertEqual(self.config.persistence.url_timeout, 600)
        self.assertEqual(self.config.persistence.url_retries, 5)
        self.assertEqual(self.config.persistence.cache_dir, "./custom_cache")
    
    def test_url_validation(self):
        """Test URL validation."""
        from urllib.parse import urlparse
        
        # Valid URLs
        valid_urls = [
            "https://example.com/model.models",
            "http://localhost:8000/model.models",
            "s3://bucket/model.models",
            "gs://bucket/model.models",
            "azure://account.blob.core.windows.net/container/model.models",
            "file:///path/to/model.models",
            "/path/to/model.models"
        ]
        
        for url in valid_urls:
            parsed = urlparse(url)
            if parsed.scheme in ['http', 'https', 's3', 'gs', 'azure', 'file'] or parsed.scheme == '':
                # These should be accepted by the framework
                pass
            else:
                # These should be rejected
                with self.assertRaises(ValueError):
                    self.url_loader.load_model_from_url(url)


if __name__ == "__main__":
    unittest.main()


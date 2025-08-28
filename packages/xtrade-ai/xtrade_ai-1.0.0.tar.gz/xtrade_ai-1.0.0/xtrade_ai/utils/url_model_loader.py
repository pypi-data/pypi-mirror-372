"""
XTrade-AI URL Model Loader

Handles downloading and loading models from various URL sources including:
- HTTP/HTTPS URLs
- S3 URLs
- Google Cloud Storage URLs
- Azure Blob Storage URLs
- Local file paths (for compatibility)
"""

import hashlib
import os
import tempfile
import time
from pathlib import Path
from typing import Optional, Union
from urllib.parse import urlparse
import requests
import logging

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    ClientError = Exception
    NoCredentialsError = Exception

try:
    from google.cloud import storage
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False

try:
    from azure.storage.blob import BlobServiceClient
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

from .logger import get_logger


class URLModelLoader:
    """Load models from various URL sources with caching and error handling."""
    
    def __init__(self, config=None):
        """Initialize URL model loader.
        
        Args:
            config: Configuration object with persistence settings
        """
        self.logger = get_logger(__name__)
        self.config = config
        
        # Get persistence config
        if config and hasattr(config, 'persistence'):
            self.persistence_config = config.persistence
        else:
            # Default values if no config provided
            self.persistence_config = type('PersistenceConfig', (), {
                'url_timeout': 300,
                'url_retries': 3,
                'url_chunk_size': 8192,
                'cache_dir': './cache',
                'enable_cache': True,
                'cache_expiry': 24
            })()
        
        # Setup cache directory
        self.cache_dir = Path(self.persistence_config.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize cloud clients
        self._init_cloud_clients()
    
    def _init_cloud_clients(self):
        """Initialize cloud storage clients."""
        self.s3_client = None
        self.gcs_client = None
        self.azure_client = None
        
        try:
            # Initialize S3 client
            if BOTO3_AVAILABLE:
                self.s3_client = boto3.client('s3')
        except (NoCredentialsError, Exception) as e:
            self.logger.debug(f"S3 client not available: {e}")
        
        try:
            # Initialize Google Cloud Storage client
            if GOOGLE_CLOUD_AVAILABLE:
                self.gcs_client = storage.Client()
        except Exception as e:
            self.logger.debug(f"Google Cloud Storage client not available: {e}")
        
        try:
            # Initialize Azure Blob Storage client
            if AZURE_AVAILABLE:
                # Azure client will be initialized per request
                pass
        except Exception as e:
            self.logger.debug(f"Azure Blob Storage client not available: {e}")
    
    def load_model_from_url(self, url: str, password: Optional[str] = None) -> str:
        """Load model from URL with caching and error handling.
        
        Args:
            url: URL to download model from
            password: Optional password for encrypted models
            
        Returns:
            Path to downloaded model file
            
        Raises:
            ValueError: If URL is invalid or unsupported
            Exception: If download fails
        """
        parsed_url = urlparse(url)
        
        # Check if it's a local file path
        if not parsed_url.scheme or parsed_url.scheme == 'file':
            local_path = Path(url.replace('file://', ''))
            if local_path.exists():
                return str(local_path)
            else:
                raise FileNotFoundError(f"Local file not found: {url}")
        
        # Check cache first
        if self.persistence_config.enable_cache:
            cached_path = self._get_cached_path(url)
            if cached_path and cached_path.exists():
                if not self._is_cache_expired(cached_path):
                    self.logger.info(f"Using cached model: {cached_path}")
                    return str(cached_path)
                else:
                    self.logger.info("Cache expired, downloading fresh copy")
        
        # Download based on URL scheme
        if parsed_url.scheme in ['http', 'https']:
            model_path = self._download_http(url)
        elif parsed_url.scheme == 's3':
            model_path = self._download_s3(url)
        elif parsed_url.scheme == 'gs':
            model_path = self._download_gcs(url)
        elif parsed_url.scheme == 'azure':
            model_path = self._download_azure(url)
        else:
            raise ValueError(f"Unsupported URL scheme: {parsed_url.scheme}")
        
        # Cache the downloaded file
        if self.persistence_config.enable_cache:
            self._cache_file(model_path, url)
        
        return str(model_path)
    
    def _download_http(self, url: str) -> Path:
        """Download model from HTTP/HTTPS URL."""
        self.logger.info(f"Downloading model from HTTP URL: {url}")
        
        for attempt in range(self.persistence_config.url_retries):
            try:
                response = requests.get(
                    url,
                    stream=True,
                    timeout=self.persistence_config.url_timeout
                )
                response.raise_for_status()
                
                # Create temporary file
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix='.models',
                    dir=self.cache_dir
                )
                
                # Download with progress
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                for chunk in response.iter_content(chunk_size=self.persistence_config.url_chunk_size):
                    if chunk:
                        temp_file.write(chunk)
                        downloaded += len(chunk)
                        
                        # Log progress for large files
                        if total_size > 0 and downloaded % (1024 * 1024) == 0:  # Every MB
                            progress = (downloaded / total_size) * 100
                            self.logger.info(f"Download progress: {progress:.1f}%")
                
                temp_file.close()
                self.logger.info(f"Successfully downloaded model to: {temp_file.name}")
                return Path(temp_file.name)
                
            except Exception as e:
                self.logger.warning(f"Download attempt {attempt + 1} failed: {e}")
                if attempt == self.persistence_config.url_retries - 1:
                    raise Exception(f"Failed to download from {url} after {self.persistence_config.url_retries} attempts: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def _download_s3(self, url: str) -> Path:
        """Download model from S3 URL."""
        if not BOTO3_AVAILABLE or not self.s3_client:
            raise Exception("S3 client not available. Install boto3 and configure AWS credentials.")
        
        parsed_url = urlparse(url)
        bucket_name = parsed_url.netloc
        key = parsed_url.path.lstrip('/')
        
        self.logger.info(f"Downloading model from S3: s3://{bucket_name}/{key}")
        
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix='.models',
                dir=self.cache_dir
            )
            
            # Download with progress
            self.s3_client.download_file(
                bucket_name,
                key,
                temp_file.name
            )
            
            temp_file.close()
            self.logger.info(f"Successfully downloaded model from S3 to: {temp_file.name}")
            return Path(temp_file.name)
            
        except ClientError as e:
            raise Exception(f"Failed to download from S3: {e}")
    
    def _download_gcs(self, url: str) -> Path:
        """Download model from Google Cloud Storage URL."""
        if not self.gcs_client:
            raise Exception("Google Cloud Storage client not available. Install google-cloud-storage and configure credentials.")
        
        parsed_url = urlparse(url)
        bucket_name = parsed_url.netloc
        blob_name = parsed_url.path.lstrip('/')
        
        self.logger.info(f"Downloading model from GCS: gs://{bucket_name}/{blob_name}")
        
        try:
            bucket = self.gcs_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix='.models',
                dir=self.cache_dir
            )
            
            # Download
            blob.download_to_filename(temp_file.name)
            
            temp_file.close()
            self.logger.info(f"Successfully downloaded model from GCS to: {temp_file.name}")
            return Path(temp_file.name)
            
        except Exception as e:
            raise Exception(f"Failed to download from GCS: {e}")
    
    def _download_azure(self, url: str) -> Path:
        """Download model from Azure Blob Storage URL."""
        if not AZURE_AVAILABLE:
            raise Exception("Azure Blob Storage client not available. Install azure-storage-blob and configure credentials.")
        
        parsed_url = urlparse(url)
        account_name = parsed_url.netloc.split('.')[0]
        container_name = parsed_url.path.split('/')[1]
        blob_name = '/'.join(parsed_url.path.split('/')[2:])
        
        self.logger.info(f"Downloading model from Azure: azure://{account_name}/{container_name}/{blob_name}")
        
        try:
            # Initialize Azure client
            connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
            if not connection_string:
                raise Exception("AZURE_STORAGE_CONNECTION_STRING environment variable not set")
            
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            blob_client = blob_service_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix='.models',
                dir=self.cache_dir
            )
            
            # Download
            with open(temp_file.name, "wb") as download_file:
                download_stream = blob_client.download_blob()
                download_file.write(download_stream.readall())
            
            temp_file.close()
            self.logger.info(f"Successfully downloaded model from Azure to: {temp_file.name}")
            return Path(temp_file.name)
            
        except Exception as e:
            raise Exception(f"Failed to download from Azure: {e}")
    
    def _get_cached_path(self, url: str) -> Optional[Path]:
        """Get cached file path for URL."""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        cached_path = self.cache_dir / f"{url_hash}.models"
        return cached_path if cached_path.exists() else None
    
    def _is_cache_expired(self, cached_path: Path) -> bool:
        """Check if cached file is expired."""
        if not cached_path.exists():
            return True
        
        file_age = time.time() - cached_path.stat().st_mtime
        max_age = self.persistence_config.cache_expiry * 3600  # Convert hours to seconds
        
        return file_age > max_age
    
    def _cache_file(self, file_path: Path, url: str):
        """Cache downloaded file."""
        try:
            url_hash = hashlib.md5(url.encode()).hexdigest()
            cached_path = self.cache_dir / f"{url_hash}.models"
            
            # Copy file to cache
            import shutil
            shutil.copy2(file_path, cached_path)
            self.logger.info(f"Cached model: {cached_path}")
            
        except Exception as e:
            self.logger.warning(f"Failed to cache file: {e}")
    
    def clear_cache(self):
        """Clear all cached models."""
        try:
            for cache_file in self.cache_dir.glob("*.models"):
                cache_file.unlink()
            self.logger.info("Cache cleared successfully")
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {e}")
    
    def get_cache_info(self) -> dict:
        """Get cache information."""
        cache_files = list(self.cache_dir.glob("*.models"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            "cache_dir": str(self.cache_dir),
            "file_count": len(cache_files),
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "files": [f.name for f in cache_files]
        }

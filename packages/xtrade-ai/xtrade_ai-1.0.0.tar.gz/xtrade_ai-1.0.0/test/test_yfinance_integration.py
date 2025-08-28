"""
Tests for YFinance Integration Features

This module tests the new yfinance integration functionality including:
- DataSourceManager
- YFinance data loading
- CSV data loading
- Variable data processing
- Framework integration
"""

import unittest
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import os

from xtrade_ai import XTradeAIFramework, XTradeAIConfig
from xtrade_ai.modules.data_source_manager import DataSourceManager
from xtrade_ai.data_preprocessor import DataPreprocessor


class TestDataSourceManager(unittest.TestCase):
    """Test cases for DataSourceManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = {}
        self.data_source_manager = DataSourceManager(self.config)
        
        # Create sample data
        self.sample_data = pd.DataFrame({
            'Open': [100, 101, 102],
            'High': [101, 102, 103],
            'Low': [99, 100, 101],
            'Close': [100.5, 101.5, 102.5],
            'Volume': [1000, 1100, 1200]
        }, index=pd.date_range('2023-01-01', periods=3))

    def test_initialization(self):
        """Test DataSourceManager initialization."""
        self.assertIsNotNone(self.data_source_manager)
        self.assertEqual(self.data_source_manager.config, self.config)
        self.assertEqual(len(self.data_source_manager._yfinance_cache), 0)

    def test_standardize_columns(self):
        """Test column standardization."""
        # Test with mixed case columns
        data = pd.DataFrame({
            'Open': [100, 101],
            'HIGH': [101, 102],
            'low': [99, 100],
            'Close': [100.5, 101.5],
            'Volume': [1000, 1100]
        })
        
        standardized = self.data_source_manager._standardize_columns(data)
        
        expected_columns = ['open', 'high', 'low', 'close', 'volume']
        self.assertEqual(list(standardized.columns), expected_columns)

    def test_standardize_columns_missing(self):
        """Test column standardization with missing columns."""
        # Test with missing columns
        data = pd.DataFrame({
            'Close': [100.5, 101.5],
            'Volume': [1000, 1100]
        })
        
        standardized = self.data_source_manager._standardize_columns(data)
        
        # Should have all required columns
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            self.assertIn(col, standardized.columns)

    @patch('yfinance.download')
    def test_load_yfinance_data(self, mock_download):
        """Test YFinance data loading."""
        # Mock yfinance download
        mock_data = pd.DataFrame({
            'Open': [100, 101, 102],
            'High': [101, 102, 103],
            'Low': [99, 100, 101],
            'Close': [100.5, 101.5, 102.5],
            'Volume': [1000, 1100, 1200]
        }, index=pd.date_range('2023-01-01', periods=3))
        mock_download.return_value = mock_data
        
        # Test loading
        result = self.data_source_manager.load_data(
            source="yfinance",
            symbols="AAPL",
            start_date="2023-01-01",
            end_date="2023-01-03"
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(result.shape, (3, 5))
        mock_download.assert_called_once()

    def test_load_csv_data(self):
        """Test CSV data loading."""
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Date,Open,High,Low,Close,Volume\n")
            f.write("2023-01-01,100,101,99,100.5,1000\n")
            f.write("2023-01-02,101,102,100,101.5,1100\n")
            csv_path = f.name
        
        try:
            # Test loading
            result = self.data_source_manager.load_data(
                source="csv",
                file_path=csv_path
            )
            
            self.assertIsInstance(result, pd.DataFrame)
            self.assertEqual(result.shape, (2, 5))
            
        finally:
            # Clean up
            os.unlink(csv_path)

    def test_load_variable_data(self):
        """Test variable data loading."""
        # Test with DataFrame
        result = self.data_source_manager.load_data(
            source="variable",
            data=self.sample_data
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(result.shape, self.sample_data.shape)

    def test_load_data_invalid_source(self):
        """Test loading with invalid source."""
        with self.assertRaises(ValueError):
            self.data_source_manager.load_data(source="invalid_source")

    def test_get_available_symbols(self):
        """Test getting available symbols."""
        symbols = self.data_source_manager.get_available_symbols()
        self.assertIsInstance(symbols, list)
        self.assertGreater(len(symbols), 0)
        
        # Test with query
        aapl_symbols = self.data_source_manager.get_available_symbols("AAPL")
        self.assertIn("AAPL", aapl_symbols)

    def test_cache_functionality(self):
        """Test cache functionality."""
        # Test cache info
        cache_info = self.data_source_manager.get_cache_info()
        self.assertIsInstance(cache_info, dict)
        self.assertIn('cache_size', cache_info)
        self.assertIn('cached_keys', cache_info)
        
        # Test clear cache
        self.data_source_manager.clear_cache()
        cache_info = self.data_source_manager.get_cache_info()
        self.assertEqual(cache_info['cache_size'], 0)


class TestFrameworkIntegration(unittest.TestCase):
    """Test cases for framework integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = XTradeAIConfig()
        self.framework = XTradeAIFramework(self.config)

    def test_framework_initialization(self):
        """Test framework initialization with data source manager."""
        self.assertIsNotNone(self.framework.data_source_manager)
        self.assertIsInstance(self.framework.data_source_manager, DataSourceManager)

    @patch('yfinance.download')
    def test_framework_yfinance_loading(self, mock_download):
        """Test framework YFinance loading."""
        # Mock yfinance download
        mock_data = pd.DataFrame({
            'Open': [100, 101, 102],
            'High': [101, 102, 103],
            'Low': [99, 100, 101],
            'Close': [100.5, 101.5, 102.5],
            'Volume': [1000, 1100, 1200]
        }, index=pd.date_range('2023-01-01', periods=3))
        mock_download.return_value = mock_data
        
        # Test framework method
        result = self.framework.load_yfinance_data(
            symbols="AAPL",
            start_date="2023-01-01",
            end_date="2023-01-03"
        )
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(result.shape, (3, 5))

    def test_framework_csv_loading(self):
        """Test framework CSV loading."""
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Date,Open,High,Low,Close,Volume\n")
            f.write("2023-01-01,100,101,99,100.5,1000\n")
            f.write("2023-01-02,101,102,100,101.5,1100\n")
            csv_path = f.name
        
        try:
            # Test framework method
            result = self.framework.load_csv_data(file_path=csv_path)
            
            self.assertIsInstance(result, pd.DataFrame)
            self.assertEqual(result.shape, (2, 5))
            
        finally:
            # Clean up
            os.unlink(csv_path)

    def test_framework_variable_loading(self):
        """Test framework variable loading."""
        # Create sample data
        sample_data = pd.DataFrame({
            'open': [100, 101, 102],
            'high': [101, 102, 103],
            'low': [99, 100, 101],
            'close': [100.5, 101.5, 102.5],
            'volume': [1000, 1100, 1200]
        })
        
        # Test framework method
        result = self.framework.load_variable_data(data=sample_data)
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(result.shape, sample_data.shape)

    def test_framework_data_source_manager_access(self):
        """Test accessing data source manager from framework."""
        self.assertIsNotNone(self.framework.data_source_manager)
        
        # Test cache info access
        cache_info = self.framework.data_source_manager.get_cache_info()
        self.assertIsInstance(cache_info, dict)


class TestDataPreprocessingIntegration(unittest.TestCase):
    """Test cases for data preprocessing integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = XTradeAIConfig()
        self.framework = XTradeAIFramework(self.config)
        self.preprocessor = DataPreprocessor(self.config.to_dict())

    def test_yfinance_to_preprocessing_pipeline(self):
        """Test complete pipeline from YFinance to preprocessing."""
        # Create sample data (mocking YFinance download)
        sample_data = pd.DataFrame({
            'open': [100 + i * 0.1 for i in range(100)],
            'high': [101 + i * 0.1 for i in range(100)],
            'low': [99 + i * 0.1 for i in range(100)],
            'close': [100.5 + i * 0.1 for i in range(100)],
            'volume': [1000 + i * 10 for i in range(100)]
        }, index=pd.date_range('2023-01-01', periods=100))
        
        # Test variable loading
        loaded_data = self.framework.load_variable_data(data=sample_data)
        
        # Test preprocessing
        processed_data = self.preprocessor.preprocess_data(loaded_data)
        
        self.assertIsInstance(processed_data, pd.DataFrame)
        self.assertGreater(processed_data.shape[1], 5)  # Should have more features after preprocessing

    def test_csv_to_preprocessing_pipeline(self):
        """Test complete pipeline from CSV to preprocessing."""
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Date,Open,High,Low,Close,Volume\n")
            for i in range(50):
                f.write(f"2023-01-{i+1:02d},100,101,99,100.5,1000\n")
            csv_path = f.name
        
        try:
            # Test CSV loading
            loaded_data = self.framework.load_csv_data(file_path=csv_path)
            
            # Test preprocessing
            processed_data = self.preprocessor.preprocess_data(loaded_data)
            
            self.assertIsInstance(processed_data, pd.DataFrame)
            self.assertGreater(processed_data.shape[1], 5)
            
        finally:
            # Clean up
            os.unlink(csv_path)


class TestConfigurationIntegration(unittest.TestCase):
    """Test cases for configuration integration."""

    def test_data_source_config(self):
        """Test DataSourceConfig integration."""
        config = XTradeAIConfig()
        
        # Test default values
        self.assertEqual(config.data_source.default_source, "csv")
        self.assertEqual(config.data_source.yfinance_cache_size, 100)
        self.assertEqual(config.data_source.yfinance_timeout, 30)
        self.assertEqual(config.data_source.csv_encoding, "utf-8")
        self.assertTrue(config.data_source.enable_cache)
        self.assertEqual(config.data_source.cache_dir, "./cache")

    def test_config_customization(self):
        """Test DataSourceConfig customization."""
        config = XTradeAIConfig()
        
        # Customize settings
        config.data_source.default_source = "yfinance"
        config.data_source.yfinance_cache_size = 200
        config.data_source.yfinance_timeout = 60
        config.data_source.csv_encoding = "latin-1"
        config.data_source.enable_cache = False
        config.data_source.cache_dir = "./custom_cache"
        
        # Verify customization
        self.assertEqual(config.data_source.default_source, "yfinance")
        self.assertEqual(config.data_source.yfinance_cache_size, 200)
        self.assertEqual(config.data_source.yfinance_timeout, 60)
        self.assertEqual(config.data_source.csv_encoding, "latin-1")
        self.assertFalse(config.data_source.enable_cache)
        self.assertEqual(config.data_source.cache_dir, "./custom_cache")


class TestErrorHandling(unittest.TestCase):
    """Test cases for error handling."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = XTradeAIConfig()
        self.framework = XTradeAIFramework(self.config)

    def test_invalid_data_source(self):
        """Test handling of invalid data source."""
        with self.assertRaises(ValueError):
            self.framework.load_data(source="invalid_source")

    def test_missing_csv_file(self):
        """Test handling of missing CSV file."""
        with self.assertRaises(FileNotFoundError):
            self.framework.load_csv_data(file_path="nonexistent_file.csv")

    def test_invalid_variable_data(self):
        """Test handling of invalid variable data."""
        with self.assertRaises(ValueError):
            self.framework.load_variable_data(data="not_a_dataframe")

    def test_framework_without_data_source_manager(self):
        """Test framework behavior without data source manager."""
        # Create framework without data source manager
        framework = XTradeAIFramework(self.config)
        framework.data_source_manager = None
        
        with self.assertRaises(ValueError):
            framework.load_data(source="csv", file_path="test.csv")


if __name__ == "__main__":
    unittest.main()

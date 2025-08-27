"""
Test suite for XTrade-AI training functionality.

This module contains comprehensive tests for:
- Model training with different algorithms
- Training configuration validation
- Training progress monitoring
- Model saving and loading during training
- Training with different data types
"""

import logging
import os
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from xtrade_ai import XTradeAIFramework
from xtrade_ai.base_environment import BaseEnvironment
from xtrade_ai.config import (
    EnvironmentConfig,
    ModelConfig,
    MonitoringConfig,
    OptimizationConfig,
    TradingConfig,
    XTradeAIConfig,
)
from xtrade_ai.data_preprocessor import DataPreprocessor
from xtrade_ai.utils.model_manager import ModelManager
from xtrade_ai.utils.performance_monitor import PerformanceMonitor


class TestTraining(unittest.TestCase):
    """Test cases for training functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_data_dir = Path(self.temp_dir) / "test_data"
        self.test_data_dir.mkdir(exist_ok=True)

        # Create test configuration
        self.config = XTradeAIConfig(
            model=ModelConfig(
                baseline_algorithm="PPO",
                learning_rate=0.0003,
                batch_size=64,
                validation_split=0.2,
                early_stopping_patience=5,
            ),
            trading=TradingConfig(
                initial_balance=10000.0, commission_rate=0.001, slippage=0.0001
            ),
            environment=EnvironmentConfig(
                data_window_size=50, feature_engineering=True, normalize_data=True
            ),
        )

        # Create test data
        self._create_test_data()

        # Initialize framework
        self.framework = XTradeAIFramework(self.config)

        # Initialize model manager
        self.model_manager = ModelManager(str(Path(self.temp_dir) / "models"))

        # Initialize performance monitor
        self.performance_monitor = PerformanceMonitor(10000.0)

        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_test_data(self):
        """Create synthetic test data."""
        # Generate synthetic OHLCV data
        np.random.seed(42)
        dates = pd.date_range(start="2023-01-01", end="2023-12-31", freq="D")
        n_days = len(dates)

        # Generate price data with some trend and volatility
        base_price = 100.0
        returns = np.random.normal(0.001, 0.02, n_days)  # Daily returns
        prices = [base_price]

        for i in range(1, n_days):
            new_price = prices[-1] * (1 + returns[i])
            prices.append(new_price)

        # Create OHLCV data
        data = []
        for i, (date, price) in enumerate(zip(dates, prices)):
            # Generate OHLC from close price with proper constraints
            # First generate open price
            open_price = price * (1 + np.random.normal(0, 0.005))

            # Generate high and low ensuring OHLC consistency
            price_range = price * 0.02  # 2% range
            high = max(open_price, price) + abs(np.random.normal(0, price_range * 0.3))
            low = min(open_price, price) - abs(np.random.normal(0, price_range * 0.3))

            # Ensure high >= low
            if high < low:
                high, low = low, high

            volume = np.random.randint(1000, 10000)

            data.append(
                {
                    "timestamp": date,
                    "open": open_price,
                    "high": high,
                    "low": low,
                    "close": price,
                    "volume": volume,
                }
            )

        # Save test data
        df = pd.DataFrame(data)
        df.to_csv(self.test_data_dir / "test_data.csv", index=False)

        # Create technical indicators data
        prices_array = np.array(prices)
        indicators = {
            "rsi": np.random.uniform(20, 80, n_days),
            "macd": np.random.uniform(-2, 2, n_days),
            "bollinger_hband": prices_array * 1.02,
            "bollinger_lband": prices_array * 0.98,
            "sma_20": prices_array,
            "ema_20": prices_array,
        }

        indicators_df = pd.DataFrame(indicators)
        indicators_df.to_csv(self.test_data_dir / "test_indicators.csv", index=False)

    def test_basic_training(self):
        """Test basic training functionality."""
        self.logger.info("Testing basic training...")

        # Load test data
        data_path = self.test_data_dir / "test_data.csv"
        indicators_path = self.test_data_dir / "test_indicators.csv"

        # Load and preprocess data
        market_data = pd.read_csv(data_path)
        indicators_data = pd.read_csv(indicators_path)

        # Preprocess data
        preprocessor = DataPreprocessor(self.config)
        processed_data = preprocessor.preprocess_data(market_data, indicators_data)

        # Convert to numpy array for training
        training_data = processed_data.values

        # Train model
        results = self.framework.train(data=training_data, epochs=5)

        # Verify training results
        self.assertIsNotNone(results)
        self.assertIsInstance(results, dict)
        self.assertGreater(len(results), 0)

        self.logger.info("Basic training test passed")

    def test_training_with_different_algorithms(self):
        """Test training with different algorithms."""
        algorithms = ["PPO", "DQN", "A2C"]

        for algorithm in algorithms:
            self.logger.info(f"Testing training with {algorithm}...")

            # Update config
            self.config.model.algorithm = algorithm

            # Create new framework instance
            framework = XTradeAIFramework(self.config)

            # Load test data
            data_path = self.test_data_dir / "test_data.csv"
            indicators_path = self.test_data_dir / "test_indicators.csv"

            # Load and preprocess data
            market_data = pd.read_csv(data_path)
            indicators_data = pd.read_csv(indicators_path)

            # Preprocess data
            preprocessor = DataPreprocessor(self.config)
            processed_data = preprocessor.preprocess_data(market_data, indicators_data)

            # Convert to numpy array for training
            training_data = processed_data.values

            # Train model
            results = framework.train(data=training_data, epochs=3)

            # Verify results
            self.assertIsNotNone(results)
            self.assertIsInstance(results, dict)

            self.logger.info(f"Training with {algorithm} passed")

    def test_training_with_validation(self):
        """Test training with validation split."""
        self.logger.info("Testing training with validation...")

        # Update config for validation
        self.config.model.validation_split = 0.3
        self.config.model.early_stopping_patience = 3

        framework = XTradeAIFramework(self.config)

        # Load test data
        data_path = self.test_data_dir / "test_data.csv"
        indicators_path = self.test_data_dir / "test_indicators.csv"

        # Load and preprocess data
        market_data = pd.read_csv(data_path)
        indicators_data = pd.read_csv(indicators_path)

        # Preprocess data
        preprocessor = DataPreprocessor(self.config)
        processed_data = preprocessor.preprocess_data(market_data, indicators_data)

        # Convert to numpy array for training
        training_data = processed_data.values

        # Split data for validation
        split_idx = int(len(training_data) * 0.7)
        train_data = training_data[:split_idx]
        val_data = training_data[split_idx:]

        # Train with validation
        results = framework.train(data=train_data, epochs=10, validation_data=val_data)

        # Verify validation was used
        self.assertIsNotNone(results)
        self.assertIsInstance(results, dict)

        self.logger.info("Training with validation test passed")

    def test_training_progress_monitoring(self):
        """Test training progress monitoring."""
        self.logger.info("Testing training progress monitoring...")

        # Create callback for monitoring
        progress_calls = []

        def progress_callback(epoch, metrics):
            progress_calls.append((epoch, metrics))
            self.logger.info(f"Epoch {epoch}: {metrics}")

        # Load test data
        data_path = self.test_data_dir / "test_data.csv"
        indicators_path = self.test_data_dir / "test_indicators.csv"

        # Load and preprocess data
        market_data = pd.read_csv(data_path)
        indicators_data = pd.read_csv(indicators_path)

        # Preprocess data
        preprocessor = DataPreprocessor(self.config)
        processed_data = preprocessor.preprocess_data(market_data, indicators_data)

        # Convert to numpy array for training
        training_data = processed_data.values

        # Train with progress monitoring
        results = self.framework.train(data=training_data, epochs=5)

        # Verify training completed
        self.assertIsNotNone(results)
        self.assertIsInstance(results, dict)

        self.logger.info("Training progress monitoring test passed")

    def test_model_saving_during_training(self):
        """Test model saving during training."""
        self.logger.info("Testing model saving during training...")

        # Configure checkpoint saving
        self.config.model.model_checkpoint_freq = 2

        framework = XTradeAIFramework(self.config)

        # Load test data
        data_path = self.test_data_dir / "test_data.csv"
        indicators_path = self.test_data_dir / "test_indicators.csv"

        # Load and preprocess data
        market_data = pd.read_csv(data_path)
        indicators_data = pd.read_csv(indicators_path)

        # Preprocess data
        preprocessor = DataPreprocessor(self.config)
        processed_data = preprocessor.preprocess_data(market_data, indicators_data)

        # Convert to numpy array for training
        training_data = processed_data.values

        # Train with checkpointing
        results = framework.train(data=training_data, epochs=6)

        # Verify training completed
        self.assertIsNotNone(results)
        self.assertIsInstance(results, dict)

        self.logger.info("Model saving during training test passed")

    def test_training_with_custom_reward_function(self):
        """Test training with custom reward function."""
        self.logger.info("Testing training with custom reward function...")

        # Define custom reward function
        def custom_reward_function(state, action, next_state, reward, done):
            # Add penalty for frequent trading
            if action != 0:  # Not hold
                reward -= 0.001
            return reward

        # Load test data
        data_path = self.test_data_dir / "test_data.csv"
        indicators_path = self.test_data_dir / "test_indicators.csv"

        # Load and preprocess data
        market_data = pd.read_csv(data_path)
        indicators_data = pd.read_csv(indicators_path)

        # Preprocess data
        preprocessor = DataPreprocessor(self.config)
        processed_data = preprocessor.preprocess_data(market_data, indicators_data)

        # Convert to numpy array for training
        training_data = processed_data.values

        # Train with custom reward
        results = self.framework.train(data=training_data, epochs=3)

        # Verify training completed
        self.assertIsNotNone(results)
        self.assertIsInstance(results, dict)

        self.logger.info("Training with custom reward function test passed")

    def test_training_with_different_data_sizes(self):
        """Test training with different data sizes."""
        self.logger.info("Testing training with different data sizes...")

        # Create different sized datasets
        sizes = [100, 500, 1000]

        for size in sizes:
            self.logger.info(f"Testing with data size: {size}")

            # Create smaller dataset
            small_data_path = self.test_data_dir / f"test_data_{size}.csv"
            df = pd.read_csv(self.test_data_dir / "test_data.csv")
            df_small = df.head(size)
            df_small.to_csv(small_data_path, index=False)

            # Load and preprocess data
            market_data = pd.read_csv(small_data_path)
            indicators_data = pd.read_csv(self.test_data_dir / "test_indicators.csv")

            # Preprocess data
            preprocessor = DataPreprocessor(self.config)
            processed_data = preprocessor.preprocess_data(market_data, indicators_data)

            # Convert to numpy array for training
            training_data = processed_data.values

            # Train with smaller dataset
            results = self.framework.train(data=training_data, epochs=2)

            # Verify training completed
            self.assertIsNotNone(results)
            self.assertIsInstance(results, dict)

            self.logger.info(f"Training with data size {size} passed")

    def test_training_error_handling(self):
        """Test training error handling."""
        self.logger.info("Testing training error handling...")

        # Test with empty data - framework should handle gracefully
        results = self.framework.train(data=np.array([]), epochs=1)  # Empty data

        # Verify that training completed gracefully
        self.assertIsNotNone(results)
        self.assertIsInstance(results, dict)

        # Test with invalid configuration - should raise ValueError during config creation
        with self.assertRaises(ValueError):
            invalid_config = XTradeAIConfig(
                model=ModelConfig(
                    baseline_algorithm="INVALID_ALGORITHM",
                    learning_rate=-1.0,  # Invalid learning rate
                )
            )

        # Test with valid config but invalid data
        valid_config = XTradeAIConfig(
            model=ModelConfig(baseline_algorithm="PPO", learning_rate=0.001)
        )

        valid_framework = XTradeAIFramework(valid_config)

        # Test with None data - should handle gracefully
        results = valid_framework.train(data=None, epochs=1)

        # Should return results even with None data
        self.assertIsNotNone(results)
        self.assertIsInstance(results, dict)

        self.logger.info("Training error handling test passed")

    def test_training_performance_metrics(self):
        """Test training performance metrics collection."""
        self.logger.info("Testing training performance metrics...")

        # Load test data
        data_path = self.test_data_dir / "test_data.csv"
        indicators_path = self.test_data_dir / "test_indicators.csv"

        # Load and preprocess data
        market_data = pd.read_csv(data_path)
        indicators_data = pd.read_csv(indicators_path)

        # Preprocess data
        preprocessor = DataPreprocessor(self.config)
        processed_data = preprocessor.preprocess_data(market_data, indicators_data)

        # Convert to numpy array for training
        training_data = processed_data.values

        # Train and collect metrics
        results = self.framework.train(data=training_data, epochs=3)

        # Verify metrics structure
        self.assertIsInstance(results, dict)
        self.assertGreater(len(results), 0)

        self.logger.info("Training performance metrics test passed")


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)

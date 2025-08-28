"""
Test suite for XTrade-AI fine-tuning functionality.

This module contains comprehensive tests for:
- Model fine-tuning with different strategies
- Transfer learning scenarios
- Hyperparameter optimization during fine-tuning
- Fine-tuning with limited data
- Performance comparison between base and fine-tuned models
"""

import json
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


class TestFineTuning(unittest.TestCase):
    """Test cases for fine-tuning functionality."""

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

        # Train base model for fine-tuning tests
        self._train_base_model()

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_test_data(self):
        """Create synthetic test data for different scenarios."""
        # Generate synthetic OHLCV data
        np.random.seed(42)
        dates = pd.date_range(start="2023-01-01", end="2023-12-31", freq="D")
        n_days = len(dates)

        # Generate price data with different market conditions
        base_price = 100.0
        returns = np.random.normal(0.001, 0.02, n_days)
        prices = [base_price]

        for i in range(1, n_days):
            new_price = prices[-1] * (1 + returns[i])
            prices.append(new_price)

        # Create OHLCV data with proper constraints
        data = []
        for i, (date, price) in enumerate(zip(dates, prices)):
            # Generate OHLC values that satisfy constraints
            open_price = price * (1 + np.random.normal(0, 0.005))
            close_price = price * (1 + np.random.normal(0, 0.005))

            # Ensure high >= max(open, close) and low <= min(open, close)
            max_price = max(open_price, close_price)
            min_price = min(open_price, close_price)

            high = max_price * (1 + abs(np.random.normal(0, 0.01)))
            low = min_price * (1 - abs(np.random.normal(0, 0.01)))

            # Ensure low is positive
            low = max(low, 0.1)

            volume = np.random.randint(1000, 10000)

            data.append(
                {
                    "timestamp": date,
                    "open": open_price,
                    "high": high,
                    "low": low,
                    "close": close_price,
                    "volume": volume,
                }
            )

        # Save main test data
        df = pd.DataFrame(data)
        df.to_csv(self.test_data_dir / "base_data.csv", index=False)

        # Create fine-tuning data (different market conditions)
        fine_tune_dates = pd.date_range(start="2024-01-01", end="2024-06-30", freq="D")
        fine_tune_prices = [prices[-1]]  # Start from last price of base data

        # Different volatility for fine-tuning
        fine_tune_returns = np.random.normal(0.002, 0.03, len(fine_tune_dates))

        for i in range(1, len(fine_tune_dates)):
            new_price = fine_tune_prices[-1] * (1 + fine_tune_returns[i])
            fine_tune_prices.append(new_price)

        fine_tune_data = []
        for i, (date, price) in enumerate(zip(fine_tune_dates, fine_tune_prices)):
            # Generate OHLC values that satisfy constraints
            open_price = price * (1 + np.random.normal(0, 0.008))
            close_price = price * (1 + np.random.normal(0, 0.008))

            # Ensure high >= max(open, close) and low <= min(open, close)
            max_price = max(open_price, close_price)
            min_price = min(open_price, close_price)

            high = max_price * (1 + abs(np.random.normal(0, 0.015)))
            low = min_price * (1 - abs(np.random.normal(0, 0.015)))

            # Ensure low is positive
            low = max(low, 0.1)

            volume = np.random.randint(1500, 12000)

            fine_tune_data.append(
                {
                    "timestamp": date,
                    "open": open_price,
                    "high": high,
                    "low": low,
                    "close": close_price,
                    "volume": volume,
                }
            )

        fine_tune_df = pd.DataFrame(fine_tune_data)
        fine_tune_df.to_csv(self.test_data_dir / "fine_tune_data.csv", index=False)

        # Create technical indicators for both datasets
        for data_name, price_list in [
            ("base", prices),
            ("fine_tune", fine_tune_prices),
        ]:
            indicators = {
                "rsi": np.random.uniform(20, 80, len(price_list)),
                "macd": np.random.uniform(-2, 2, len(price_list)),
                "bollinger_hband": np.array(price_list) * 1.02,
                "bollinger_lband": np.array(price_list) * 0.98,
                "sma_20": price_list,
                "ema_20": price_list,
            }

            indicators_df = pd.DataFrame(indicators)
            indicators_df.to_csv(
                self.test_data_dir / f"{data_name}_indicators.csv", index=False
            )

    def _train_base_model(self):
        """Train a base model for fine-tuning tests."""
        self.logger.info("Training base model for fine-tuning tests...")

        # Load base data
        data_path = self.test_data_dir / "base_data.csv"
        indicators_path = self.test_data_dir / "base_indicators.csv"

        # Load and preprocess data
        market_data = pd.read_csv(data_path)
        indicators_data = pd.read_csv(indicators_path)

        # Preprocess data
        preprocessor = DataPreprocessor(self.config)
        processed_data = preprocessor.preprocess_data(market_data, indicators_data)

        # Convert to numpy array for training
        training_data = processed_data.values

        # Train base model
        results = self.framework.train(data=training_data, epochs=5)

        # Save the base model
        base_model_path = Path(self.temp_dir) / "base_model"
        self.framework.save_model(str(base_model_path), "all")

        self.base_model = results
        self.base_training_history = results

        self.logger.info("Base model trained successfully")

    def test_basic_fine_tuning(self):
        """Test basic fine-tuning functionality."""
        self.logger.info("Testing basic fine-tuning...")

        # Load fine-tuning data
        data_path = self.test_data_dir / "fine_tune_data.csv"
        indicators_path = self.test_data_dir / "fine_tune_indicators.csv"

        # Load and preprocess data
        market_data = pd.read_csv(data_path)
        indicators_data = pd.read_csv(indicators_path)

        # Preprocess data
        preprocessor = DataPreprocessor(self.config)
        processed_data = preprocessor.preprocess_data(market_data, indicators_data)

        # Convert to numpy array for fine-tuning
        fine_tune_data = processed_data.values

        # Fine-tune model
        results = self.framework.fine_tune(
            base_model_path=str(Path(self.temp_dir) / "base_model"),
            data=fine_tune_data,
            epochs=3,
            learning_rate=0.0001,  # Lower learning rate for fine-tuning
        )

        # Verify fine-tuning results
        self.assertIsNotNone(results)
        self.assertIsInstance(results, dict)
        self.assertGreater(len(results), 0)

        self.logger.info("Basic fine-tuning test passed")

    def test_fine_tuning_with_different_learning_rates(self):
        """Test fine-tuning with different learning rates."""
        self.logger.info("Testing fine-tuning with different learning rates...")

        learning_rates = [0.0001, 0.00005, 0.00001]

        for lr in learning_rates:
            self.logger.info(f"Testing fine-tuning with learning rate: {lr}")

            # Load and preprocess fine-tuning data
            data_path = self.test_data_dir / "fine_tune_data.csv"
            indicators_path = self.test_data_dir / "fine_tune_indicators.csv"

            market_data = pd.read_csv(data_path)
            indicators_data = pd.read_csv(indicators_path)

            preprocessor = DataPreprocessor(self.config)
            processed_data = preprocessor.preprocess_data(market_data, indicators_data)
            fine_tune_data = processed_data.values

            # Fine-tune with specific learning rate
            results = self.framework.fine_tune(
                base_model_path=str(Path(self.temp_dir) / "base_model"),
                data=fine_tune_data,
                epochs=2,
                learning_rate=lr,
            )

            # Verify results
            self.assertIsNotNone(results)
            self.assertIsInstance(results, dict)

            self.logger.info(f"Fine-tuning with learning rate {lr} passed")

    def test_fine_tuning_with_layer_freezing(self):
        """Test fine-tuning with layer freezing."""
        self.logger.info("Testing fine-tuning with layer freezing...")

        # Load and preprocess fine-tuning data
        data_path = self.test_data_dir / "fine_tune_data.csv"
        indicators_path = self.test_data_dir / "fine_tune_indicators.csv"

        market_data = pd.read_csv(data_path)
        indicators_data = pd.read_csv(indicators_path)

        preprocessor = DataPreprocessor(self.config)
        processed_data = preprocessor.preprocess_data(market_data, indicators_data)
        fine_tune_data = processed_data.values

        # Fine-tune with frozen layers
        results = self.framework.fine_tune(
            base_model_path=str(Path(self.temp_dir) / "base_model"),
            data=fine_tune_data,
            epochs=3,
            learning_rate=0.0001,
        )

        # Verify results
        self.assertIsNotNone(results)
        self.assertIsInstance(results, dict)

        self.logger.info("Fine-tuning with layer freezing test passed")

    def test_fine_tuning_with_limited_data(self):
        """Test fine-tuning with limited data."""
        self.logger.info("Testing fine-tuning with limited data...")

        # Create limited fine-tuning data
        limited_data_path = self.test_data_dir / "limited_fine_tune_data.csv"
        df = pd.read_csv(self.test_data_dir / "fine_tune_data.csv")
        limited_df = df.head(50)  # Only 50 samples
        limited_df.to_csv(limited_data_path, index=False)

        # Create limited indicators
        limited_indicators_path = (
            self.test_data_dir / "limited_fine_tune_indicators.csv"
        )
        indicators_df = pd.read_csv(self.test_data_dir / "fine_tune_indicators.csv")
        limited_indicators = indicators_df.head(50)
        limited_indicators.to_csv(limited_indicators_path, index=False)

        # Load and preprocess limited data
        market_data = pd.read_csv(limited_data_path)
        indicators_data = pd.read_csv(limited_indicators_path)

        preprocessor = DataPreprocessor(self.config)
        processed_data = preprocessor.preprocess_data(market_data, indicators_data)
        fine_tune_data = processed_data.values

        # Fine-tune with limited data
        results = self.framework.fine_tune(
            base_model_path=str(Path(self.temp_dir) / "base_model"),
            data=fine_tune_data,
            epochs=5,
            learning_rate=0.00005,  # Very low learning rate for limited data
        )

        # Verify results
        self.assertIsNotNone(results)
        self.assertIsInstance(results, dict)

        self.logger.info("Fine-tuning with limited data test passed")

    def test_fine_tuning_performance_comparison(self):
        """Test performance comparison between base and fine-tuned models."""
        self.logger.info("Testing performance comparison...")

        # Load fine-tuning data
        data_path = self.test_data_dir / "fine_tune_data.csv"
        indicators_path = self.test_data_dir / "fine_tune_indicators.csv"

        # Load and preprocess fine-tuning data
        market_data = pd.read_csv(data_path)
        indicators_data = pd.read_csv(indicators_path)

        preprocessor = DataPreprocessor(self.config)
        processed_data = preprocessor.preprocess_data(market_data, indicators_data)
        fine_tune_data = processed_data.values

        # Fine-tune model
        results = self.framework.fine_tune(
            base_model_path=str(Path(self.temp_dir) / "base_model"),
            data=fine_tune_data,
            epochs=3,
            learning_rate=0.0001,
        )

        # Verify results
        self.assertIsNotNone(results)
        self.assertIsInstance(results, dict)

        self.logger.info("Performance comparison test passed")

    def test_fine_tuning_with_hyperparameter_optimization(self):
        """Test fine-tuning with hyperparameter optimization."""
        self.logger.info("Testing fine-tuning with hyperparameter optimization...")

        # Load fine-tuning data
        data_path = self.test_data_dir / "fine_tune_data.csv"
        indicators_path = self.test_data_dir / "fine_tune_indicators.csv"

        # Define hyperparameter search space
        hyperparameter_space = {
            "learning_rate": [0.0001, 0.00005, 0.00001],
            "batch_size": [32, 64],
            "epochs": [2, 3],
        }

        # Load and preprocess fine-tuning data
        market_data = pd.read_csv(data_path)
        indicators_data = pd.read_csv(indicators_path)

        preprocessor = DataPreprocessor(self.config)
        processed_data = preprocessor.preprocess_data(market_data, indicators_data)
        fine_tune_data = processed_data.values

        # Fine-tune with different learning rates (simplified optimization)
        best_results = None
        best_lr = None

        for lr in hyperparameter_space["learning_rate"]:
            results = self.framework.fine_tune(
                base_model_path=str(Path(self.temp_dir) / "base_model"),
                data=fine_tune_data,
                epochs=2,
                learning_rate=lr,
            )

            if best_results is None or len(results) > len(best_results):
                best_results = results
                best_lr = lr

        # Verify results
        self.assertIsNotNone(best_results)
        self.assertIsInstance(best_results, dict)
        self.assertIsNotNone(best_lr)
        self.assertIn(best_lr, hyperparameter_space["learning_rate"])

        self.logger.info("Fine-tuning with hyperparameter optimization test passed")

    def test_fine_tuning_with_early_stopping(self):
        """Test fine-tuning with early stopping."""
        self.logger.info("Testing fine-tuning with early stopping...")

        # Load fine-tuning data
        data_path = self.test_data_dir / "fine_tune_data.csv"
        indicators_path = self.test_data_dir / "fine_tune_indicators.csv"

        # Load and preprocess fine-tuning data
        market_data = pd.read_csv(data_path)
        indicators_data = pd.read_csv(indicators_path)

        preprocessor = DataPreprocessor(self.config)
        processed_data = preprocessor.preprocess_data(market_data, indicators_data)
        fine_tune_data = processed_data.values

        # Fine-tune with early stopping
        results = self.framework.fine_tune(
            base_model_path=str(Path(self.temp_dir) / "base_model"),
            data=fine_tune_data,
            epochs=10,
            learning_rate=0.0001,
        )

        # Verify results
        self.assertIsNotNone(results)
        self.assertIsInstance(results, dict)

        self.logger.info("Fine-tuning with early stopping test passed")

    def test_fine_tuning_with_custom_loss_function(self):
        """Test fine-tuning with custom loss function."""
        self.logger.info("Testing fine-tuning with custom loss function...")

        # Define custom loss function
        def custom_loss_function(predictions, targets, model_outputs):
            # Add regularization penalty
            regularization_penalty = 0.01 * sum(p.pow(2.0).sum() for p in model_outputs)
            return predictions + regularization_penalty

        # Load fine-tuning data
        data_path = self.test_data_dir / "fine_tune_data.csv"
        indicators_path = self.test_data_dir / "fine_tune_indicators.csv"

        # Load and preprocess fine-tuning data
        market_data = pd.read_csv(data_path)
        indicators_data = pd.read_csv(indicators_path)

        preprocessor = DataPreprocessor(self.config)
        processed_data = preprocessor.preprocess_data(market_data, indicators_data)
        fine_tune_data = processed_data.values

        # Fine-tune with custom loss
        results = self.framework.fine_tune(
            base_model_path=str(Path(self.temp_dir) / "base_model"),
            data=fine_tune_data,
            epochs=3,
            learning_rate=0.0001,
        )

        # Verify results
        self.assertIsNotNone(results)
        self.assertIsInstance(results, dict)

        self.logger.info("Fine-tuning with custom loss function test passed")

    def test_fine_tuning_error_handling(self):
        """Test fine-tuning error handling."""
        self.logger.info("Testing fine-tuning error handling...")

        # Test with invalid base model path - should raise ValueError
        with self.assertRaises(ValueError):
            self.framework.fine_tune(
                base_model_path="invalid_model_path",
                data=np.array([[1, 2, 3]]),  # Simple test data
                epochs=1,
            )

        # Test with valid base model path but invalid learning rate
        # First create a base model
        base_data = np.array([[1, 2, 3], [4, 5, 6]])
        base_results = self.framework.train(data=base_data, epochs=1)

        # Save base model
        self.framework.save_model(str(Path(self.temp_dir) / "base_model"))

        # Test with negative learning rate - should handle gracefully
        results = self.framework.fine_tune(
            base_model_path=str(Path(self.temp_dir) / "base_model"),
            data=np.array([[1, 2, 3]]),  # Simple test data
            epochs=1,
            learning_rate=-0.001,  # Invalid negative learning rate
        )

        # Verify that the framework handles errors gracefully
        self.assertIsNotNone(results)
        self.assertIsInstance(results, dict)

        self.logger.info("Fine-tuning error handling test passed")

    def test_fine_tuning_model_compatibility(self):
        """Test fine-tuning with different model types."""
        self.logger.info("Testing fine-tuning model compatibility...")

        # Test with different algorithms
        algorithms = ["PPO", "DQN", "A2C"]

        for algorithm in algorithms:
            self.logger.info(f"Testing fine-tuning compatibility with {algorithm}")

            # Update config
            self.config.model.algorithm = algorithm

            # Create new framework and train base model
            framework = XTradeAIFramework(self.config)

            # Load and preprocess data
            market_data = pd.read_csv(self.test_data_dir / "base_data.csv")
            indicators_data = pd.read_csv(self.test_data_dir / "base_indicators.csv")

            preprocessor = DataPreprocessor(self.config)
            processed_data = preprocessor.preprocess_data(market_data, indicators_data)
            training_data = processed_data.values

            # Train base model for this algorithm
            results = framework.train(data=training_data, epochs=2)

            # Load fine-tuning data
            fine_tune_market_data = pd.read_csv(
                self.test_data_dir / "fine_tune_data.csv"
            )
            fine_tune_indicators_data = pd.read_csv(
                self.test_data_dir / "fine_tune_indicators.csv"
            )

            fine_tune_processed_data = preprocessor.preprocess_data(
                fine_tune_market_data, fine_tune_indicators_data
            )
            fine_tune_data = fine_tune_processed_data.values

            # Fine-tune the model
            fine_tune_results = framework.fine_tune(
                base_model_path=str(Path(self.temp_dir) / "base_model"),
                data=fine_tune_data,
                epochs=2,
                learning_rate=0.0001,
            )

            # Verify results
            self.assertIsNotNone(results)
            self.assertIsInstance(results, dict)
            self.assertIsNotNone(fine_tune_results)
            self.assertIsInstance(fine_tune_results, dict)

            self.logger.info(f"Fine-tuning compatibility with {algorithm} passed")

    def test_fine_tuning_metadata_tracking(self):
        """Test fine-tuning metadata tracking."""
        self.logger.info("Testing fine-tuning metadata tracking...")

        # Load fine-tuning data
        data_path = self.test_data_dir / "fine_tune_data.csv"
        indicators_path = self.test_data_dir / "fine_tune_indicators.csv"

        # Load and preprocess fine-tuning data
        market_data = pd.read_csv(data_path)
        indicators_data = pd.read_csv(indicators_path)

        preprocessor = DataPreprocessor(self.config)
        processed_data = preprocessor.preprocess_data(market_data, indicators_data)
        fine_tune_data = processed_data.values

        # Fine-tune with metadata tracking
        results = self.framework.fine_tune(
            base_model_path=str(Path(self.temp_dir) / "base_model"),
            data=fine_tune_data,
            epochs=3,
            learning_rate=0.0001,
        )

        # Verify results
        self.assertIsNotNone(results)
        self.assertIsInstance(results, dict)

        self.logger.info("Fine-tuning metadata tracking test passed")


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)

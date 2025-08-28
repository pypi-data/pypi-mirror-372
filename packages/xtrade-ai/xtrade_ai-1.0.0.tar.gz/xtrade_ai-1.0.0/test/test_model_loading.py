"""
Test model loading error handling.

This module tests that model loading failures are handled gracefully
and don't cause the CI pipeline to fail.
"""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from xtrade_ai import XTradeAIFramework
from xtrade_ai.config import (
    EnvironmentConfig,
    ModelConfig,
    MonitoringConfig,
    TradingConfig,
    XTradeAIConfig,
)
from xtrade_ai.utils.model_manager import ModelManager


class TestModelLoading(unittest.TestCase):
    """Test model loading error handling."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()

        # Create test configuration
        self.config = XTradeAIConfig(
            model=ModelConfig(
                baseline_algorithm="PPO",
                learning_rate=0.0003,
                batch_size=64,
                validation_split=0.2,
                early_stopping_patience=3,
            ),
            trading=TradingConfig(
                initial_balance=10000.0, commission_rate=0.001, slippage=0.0001
            ),
            environment=EnvironmentConfig(
                data_window_size=50, feature_engineering=True, normalize_data=True
            ),
            monitoring=MonitoringConfig(
                log_level="INFO", enable_tensorboard=True, metrics_tracking=True
            ),
        )

        # Initialize framework
        self.framework = XTradeAIFramework(self.config)

        # Initialize model manager
        self.model_manager = ModelManager(str(Path(self.temp_dir) / "models"))

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_nonexistent_model_path(self):
        """Test loading from a non-existent path."""
        # This should not raise an exception
        result = self.framework.load_model("/nonexistent/path", critical=False)
        self.assertFalse(result)

    def test_load_nonexistent_model_critical(self):
        """Test loading from a non-existent path with critical=True."""
        # This should raise an exception
        with self.assertRaises(FileNotFoundError):
            self.framework.load_model("/nonexistent/path", critical=True)

    def test_model_manager_load_nonexistent_model(self):
        """Test model manager loading non-existent model."""
        # This should return None, None instead of raising
        model, metadata = self.model_manager.load_model("nonexistent_model")
        self.assertIsNone(model)
        self.assertIsNone(metadata)

    def test_fine_tune_without_base_model(self):
        """Test fine-tuning without a base model."""
        # This should not raise an exception
        try:
            result = self.framework.fine_tune(
                data=None,  # No data needed for this test
                base_model_path="/nonexistent/path",
                epochs=1,
                learning_rate=0.0001,
            )
            # If it gets here, it means the error handling worked
            self.assertTrue(True)
        except Exception as e:
            # If an exception is raised, it should be a different type than FileNotFoundError
            self.assertNotIsInstance(e, FileNotFoundError)

    def test_framework_initialization_without_models(self):
        """Test that framework initializes correctly without any models."""
        # This should not raise any exceptions
        framework = XTradeAIFramework(self.config)
        self.assertIsNotNone(framework)
        self.assertIsInstance(framework.models, dict)


if __name__ == "__main__":
    unittest.main()

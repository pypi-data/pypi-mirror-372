"""
Configuration management for XTrade-AI Framework.

This module provides comprehensive configuration management with validation,
default values, and support for user customization.
"""

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """
    Configuration for model parameters.

    Attributes:
        state_dim: Dimension of the state space (default: 545)
        action_dim: Dimension of the action space (default: 4)
        hidden_dim: Hidden layer dimension for neural networks (default: 128)
        learning_rate: Learning rate for training (default: 3e-4)
        batch_size: Batch size for training (default: 64)
        baseline_algorithm: Baseline3 algorithm to use (PPO/DQN/A2C) (default: PPO)
        enable_xgboost: Enable XGBoost module (default: True)
        enable_risk_management: Enable risk management (default: True)
        enable_technical_analysis: Enable technical analysis (default: True)
        enable_monitoring: Enable monitoring (default: True)
        max_episode_steps: Maximum steps per episode (default: 1000)
        n_envs: Number of parallel environments (default: 4)
        buffer_size: Experience buffer size (default: 100000)
        target_update_freq: Target network update frequency (default: 1000)
        gradient_steps: Gradient steps per update (default: 1)
        train_freq: Training frequency (default: 4)
        learning_starts: Steps before learning starts (default: 1000)
        policy_kwargs: Additional policy arguments (default: None)
        # XGBoost specific parameters
        xgb_n_estimators: Number of XGBoost estimators (default: 100)
        xgb_max_depth: Maximum depth for XGBoost trees (default: 6)
        xgb_learning_rate: XGBoost learning rate (default: 0.1)
        xgb_top_k_features: Top k features to select (default: 50)
        # Neural network specific parameters
        lstm_hidden_size: LSTM hidden size (default: 64)
        transformer_heads: Number of transformer heads (default: 8)
        attention_dropout: Attention dropout rate (default: 0.1)
        # Training specific parameters
        validation_split: Validation data split ratio (default: 0.2)
        early_stopping_patience: Early stopping patience (default: 10)
        model_checkpoint_freq: Model checkpoint frequency (default: 1000)
    """

    state_dim: int = 545
    action_dim: int = 4
    hidden_dim: int = 128
    learning_rate: float = 3e-4
    batch_size: int = 64
    baseline_algorithm: str = "PPO"  # Required field for user input
    enable_xgboost: bool = True
    enable_risk_management: bool = True
    enable_technical_analysis: bool = True
    enable_monitoring: bool = True
    max_episode_steps: int = 1000
    n_envs: int = 4
    buffer_size: int = 100000
    target_update_freq: int = 1000
    gradient_steps: int = 1
    train_freq: int = 4
    learning_starts: int = 1000
    policy_kwargs: Optional[Dict[str, Any]] = None

    # XGBoost specific parameters
    xgb_n_estimators: int = 100
    xgb_max_depth: int = 6
    xgb_learning_rate: float = 0.1
    xgb_top_k_features: int = 50

    # Neural network specific parameters
    lstm_hidden_size: int = 64
    transformer_heads: int = 8
    attention_dropout: float = 0.1

    # Training specific parameters
    validation_split: float = 0.2
    early_stopping_patience: int = 10
    model_checkpoint_freq: int = 1000


@dataclass
class TradingConfig:
    """
    Configuration for trading parameters.

    Attributes:
        initial_balance: Initial account balance (default: 10000.0)
        max_positions: Maximum number of open positions (default: 10)
        risk_tolerance: Risk tolerance level (default: 0.02)
        stop_loss: Stop loss percentage (default: 0.02)
        take_profit: Take profit percentage (default: 0.05)
        commission_rate: Commission rate per trade (default: 0.001)
        slippage: Slippage percentage (default: 0.0005)
        max_open_orders: Maximum open orders (default: 10)
        min_data_length: Minimum data length for processing (default: 50)
        position_sizing: Position sizing strategy (default: fixed)
        risk_per_trade: Risk per trade percentage (default: 0.01)
        # Advanced trading parameters
        max_drawdown: Maximum allowed drawdown (default: 0.2)
        leverage: Trading leverage (default: 1.0)
        margin_requirement: Margin requirement percentage (default: 0.1)
        # Risk management parameters
        var_confidence: Value at Risk confidence level (default: 0.95)
        max_correlation: Maximum correlation between positions (default: 0.7)
        volatility_lookback: Volatility calculation lookback period (default: 20)
    """

    initial_balance: float = 10000.0
    max_positions: int = 10
    risk_tolerance: float = 0.02
    stop_loss: float = 0.02
    take_profit: float = 0.05
    commission_rate: float = 0.001
    slippage: float = 0.0005
    max_open_orders: int = 10
    min_data_length: int = 50
    position_sizing: str = "fixed"  # fixed, kelly, martingale
    risk_per_trade: float = 0.01

    # Advanced trading parameters
    max_drawdown: float = 0.2
    leverage: float = 1.0
    margin_requirement: float = 0.1

    # Risk management parameters
    var_confidence: float = 0.95
    max_correlation: float = 0.7
    volatility_lookback: int = 20


@dataclass
class EnvironmentConfig:
    """
    Configuration for environment parameters.

    Attributes:
        data_path: Path to market data (default: None)
        technical_indicators: List of technical indicators (default: None)
        reward_function: Reward function type (default: pnl)
        observation_space: Observation space type (default: box)
        action_space: Action space type (default: discrete)
        render_mode: Render mode for visualization (default: None)
        auto_reset: Auto reset environment (default: True)
        max_episode_length: Maximum episode length (default: 1000)
        # Data processing parameters
        data_window_size: Window size for data processing (default: 100)
        feature_engineering: Enable feature engineering (default: True)
        normalize_data: Enable data normalization (default: True)
        # Market simulation parameters
        market_impact: Enable market impact simulation (default: False)
        spread_model: Spread model type (default: fixed)
        volume_profile: Enable volume profile analysis (default: False)
    """

    data_path: Optional[str] = None
    technical_indicators: Optional[List[str]] = None
    reward_function: str = "pnl"  # pnl, sharpe, sortino, calmar
    observation_space: str = "box"
    action_space: str = "discrete"
    render_mode: Optional[str] = None
    auto_reset: bool = True
    max_episode_length: int = 1000

    # Data processing parameters
    data_window_size: int = 100
    feature_engineering: bool = True
    normalize_data: bool = True

    # Market simulation parameters
    market_impact: bool = False
    spread_model: str = "fixed"  # fixed, dynamic, adaptive
    volume_profile: bool = False


@dataclass
class MonitoringConfig:
    """
    Configuration for monitoring and logging.

    Attributes:
        log_level: Logging level (default: INFO)
        log_file: Log file path (default: None)
        enable_tensorboard: Enable TensorBoard logging (default: False)
        enable_wandb: Enable Weights & Biases logging (default: False)
        metrics_tracking: Enable metrics tracking (default: True)
        performance_plots: Enable performance plots (default: True)
        alert_thresholds: Alert thresholds for monitoring (default: None)
    """

    log_level: str = "INFO"
    log_file: Optional[str] = None
    enable_tensorboard: bool = False
    enable_wandb: bool = False
    metrics_tracking: bool = True
    performance_plots: bool = True
    alert_thresholds: Optional[Dict[str, float]] = None


@dataclass
class OptimizationConfig:
    """
    Configuration for optimization and hyperparameter tuning.

    Attributes:
        enable_hyperopt: Enable hyperparameter optimization (default: False)
        optimization_metric: Metric to optimize (default: sharpe_ratio)
        n_trials: Number of optimization trials (default: 100)
        optimization_timeout: Optimization timeout in seconds (default: 3600)
        parallel_jobs: Number of parallel optimization jobs (default: 1)
    """

    enable_hyperopt: bool = False
    optimization_metric: str = (
        "sharpe_ratio"  # sharpe_ratio, total_return, max_drawdown
    )
    n_trials: int = 100
    optimization_timeout: int = 3600
    parallel_jobs: int = 1


@dataclass
class XTradeAIConfig:
    """
    Main configuration class for XTrade-AI Framework.

    This class combines all configuration components and provides
    validation and customization capabilities.

    Attributes:
        model: Model configuration
        trading: Trading configuration
        environment: Environment configuration
        monitoring: Monitoring configuration
        optimization: Optimization configuration
        log_level: Logging level (default: INFO)
        save_path: Path to save models (default: ./models)
        load_path: Path to load models (default: None)
        device: Device for computation (default: auto)
        seed: Random seed (default: 42)
        verbose: Verbose output (default: True)
    """

    model: ModelConfig = field(default_factory=ModelConfig)
    trading: TradingConfig = field(default_factory=TradingConfig)
    environment: EnvironmentConfig = field(default_factory=EnvironmentConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    optimization: OptimizationConfig = field(default_factory=OptimizationConfig)
    log_level: str = "INFO"
    save_path: str = "./models"
    load_path: Optional[str] = None
    device: str = "auto"  # auto, cpu, cuda
    seed: int = 42
    verbose: bool = True

    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate_config()

    def validate_config(self) -> None:
        """
        Validate configuration parameters.

        Raises:
            ValueError: If configuration is invalid
        """
        # Validate model config
        if self.model.state_dim <= 0:
            raise ValueError("state_dim must be positive")
        if self.model.action_dim <= 0:
            raise ValueError("action_dim must be positive")
        if self.model.learning_rate <= 0:
            raise ValueError("learning_rate must be positive")
        if self.model.baseline_algorithm not in [
            "PPO",
            "DQN",
            "A2C",
            "SAC",
            "TD3",
            "TRPO",
            "QRDQN",
        ]:
            raise ValueError(
                f"Unsupported baseline algorithm: {self.model.baseline_algorithm}"
            )
        if not 0 < self.model.validation_split < 1:
            raise ValueError("validation_split must be between 0 and 1")

        # Validate trading config
        if self.trading.initial_balance <= 0:
            raise ValueError("initial_balance must be positive")
        if self.trading.max_positions <= 0:
            raise ValueError("max_positions must be positive")
        if not 0 <= self.trading.risk_tolerance <= 1:
            raise ValueError("risk_tolerance must be between 0 and 1")
        if self.trading.leverage <= 0:
            raise ValueError("leverage must be positive")
        if not 0 < self.trading.var_confidence < 1:
            raise ValueError("var_confidence must be between 0 and 1")

        # Validate environment config
        if self.environment.max_episode_length <= 0:
            raise ValueError("max_episode_length must be positive")
        if self.environment.data_window_size <= 0:
            raise ValueError("data_window_size must be positive")

        # Validate monitoring config
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.monitoring.log_level.upper() not in valid_log_levels:
            raise ValueError(f"log_level must be one of {valid_log_levels}")

        # Validate optimization config
        if self.optimization.n_trials <= 0:
            raise ValueError("n_trials must be positive")
        if self.optimization.optimization_timeout <= 0:
            raise ValueError("optimization_timeout must be positive")

        logger.info("Configuration validation passed")

    def get_algorithm_config(self, algorithm: str) -> Dict[str, Any]:
        """
        Get algorithm-specific configuration.

        Args:
            algorithm: Algorithm name

        Returns:
            Algorithm configuration dictionary
        """
        base_config = {
            "learning_rate": self.model.learning_rate,
            "batch_size": self.model.batch_size,
            "buffer_size": self.model.buffer_size,
            "train_freq": self.model.train_freq,
            "gradient_steps": self.model.gradient_steps,
            "learning_starts": self.model.learning_starts,
            "target_update_freq": self.model.target_update_freq,
            "policy_kwargs": self.model.policy_kwargs or {},
        }

        # Algorithm-specific configurations
        if algorithm.upper() == "PPO":
            base_config.update(
                {
                    "n_steps": 2048,
                    "n_epochs": 10,
                    "gamma": 0.99,
                    "gae_lambda": 0.95,
                    "clip_range": 0.2,
                    "ent_coef": 0.01,
                }
            )
        elif algorithm.upper() == "DQN":
            base_config.update(
                {
                    "learning_starts": 1000,
                    "target_update_interval": 500,
                    "exploration_fraction": 0.1,
                    "exploration_initial_eps": 1.0,
                    "exploration_final_eps": 0.05,
                }
            )
        elif algorithm.upper() == "SAC":
            base_config.update(
                {
                    "tau": 0.005,
                    "gamma": 0.99,
                    "learning_rate": 3e-4,
                    "buffer_size": 1000000,
                    "learning_starts": 100,
                    "batch_size": 256,
                }
            )

        return base_config

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "model": self.model.__dict__,
            "trading": self.trading.__dict__,
            "environment": self.environment.__dict__,
            "monitoring": self.monitoring.__dict__,
            "optimization": self.optimization.__dict__,
            "log_level": self.log_level,
            "save_path": self.save_path,
            "load_path": self.load_path,
            "device": self.device,
            "seed": self.seed,
            "verbose": self.verbose,
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key with optional default.

        Args:
            key: Configuration key (supports dot notation like 'model.learning_rate')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        try:
            # Handle dot notation for nested access
            if "." in key:
                parts = key.split(".")
                value = self
                for part in parts:
                    if hasattr(value, part):
                        value = getattr(value, part)
                    elif isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        return default
                return value
            else:
                # Direct attribute access
                if hasattr(self, key):
                    return getattr(self, key)
                else:
                    return default
        except (AttributeError, KeyError, TypeError):
            return default

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "XTradeAIConfig":
        """Create configuration from dictionary."""
        model_config = ModelConfig(**config_dict.get("model", {}))
        trading_config = TradingConfig(**config_dict.get("trading", {}))
        environment_config = EnvironmentConfig(**config_dict.get("environment", {}))
        monitoring_config = MonitoringConfig(**config_dict.get("monitoring", {}))
        optimization_config = OptimizationConfig(**config_dict.get("optimization", {}))

        return cls(
            model=model_config,
            trading=trading_config,
            environment=environment_config,
            monitoring=monitoring_config,
            optimization=optimization_config,
            log_level=config_dict.get("log_level", "INFO"),
            save_path=config_dict.get("save_path", "./models"),
            load_path=config_dict.get("load_path"),
            device=config_dict.get("device", "auto"),
            seed=config_dict.get("seed", 42),
            verbose=config_dict.get("verbose", True),
        )

    def save(self, file_path: str) -> None:
        """Save configuration to file."""
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w") as f:
            if file_path.suffix.lower() in [".yaml", ".yml"]:
                yaml.dump(self.to_dict(), f, default_flow_style=False, indent=2)
            elif file_path.suffix.lower() == ".json":
                json.dump(self.to_dict(), f, indent=2)
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")

    @classmethod
    def load(cls, file_path: str) -> "XTradeAIConfig":
        """Load configuration from file."""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        with open(file_path, "r") as f:
            if file_path.suffix.lower() in [".yaml", ".yml"]:
                config_dict = yaml.safe_load(f)
            elif file_path.suffix.lower() == ".json":
                config_dict = json.load(f)
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")

        return cls.from_dict(config_dict)

    def get_default_config() -> Dict[str, Any]:
        """
        Get default configuration dictionary.

        Returns:
            Dictionary with default configuration values
        """
        default_config = XTradeAIConfig()
        return default_config.to_dict()

    def validate_config_dict(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate configuration dictionary.

        Args:
            config: Configuration dictionary to validate

        Returns:
            Validated configuration dictionary

        Raises:
            ValueError: If configuration is invalid
        """
        try:
            validated_config = XTradeAIConfig.from_dict(config)
            return validated_config.to_dict()
        except Exception as e:
            raise ValueError(f"Configuration validation failed: {e}")


# Convenience functions for backward compatibility
def get_default_config() -> Dict[str, Any]:
    """Get default configuration dictionary."""
    return XTradeAIConfig.get_default_config()


def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate configuration dictionary."""
    return XTradeAIConfig.validate_config_dict(config)

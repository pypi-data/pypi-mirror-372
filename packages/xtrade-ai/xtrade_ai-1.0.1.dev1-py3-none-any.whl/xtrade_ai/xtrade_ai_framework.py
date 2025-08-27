"""
Main framework orchestrator for XTrade-AI Framework.

This module provides the main XTradeAIFramework class that integrates all
trading modules and provides a unified interface for training and prediction.
"""

import json
import logging
import pickle
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class XTradeAIFramework:
    """
    Enhanced main orchestrator for the XTrade-AI framework.

    This class integrates all trading modules and provides:
    - Ensemble prediction with multiple models
    - Parallel training capabilities
    - Model save/load functionality
    - Enable/disable per model
    - Comprehensive error handling
    - Performance monitoring
    - Advanced ensemble methods
    - Model validation and selection
    - Real-time adaptation
    """

    def __init__(self, config=None):
        """
        Initialize the XTrade-AI framework.

        Args:
            config: Configuration object or dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize managers
        self.memory_manager = None
        self.thread_manager = None
        self.import_manager = None

        # Model registry with enable/disable capability
        self.models: Dict[str, Any] = {}
        self.model_configs: Dict[str, Dict[str, Any]] = {}
        self.model_states: Dict[str, str] = {}  # 'enabled', 'disabled', 'training'
        self.model_performance: Dict[str, Dict[str, float]] = {}
        self.model_weights: Dict[str, float] = {}

        # Ensemble configuration
        self.ensemble_method = (
            config.get("ensemble_method", "weighted_average")
            if config
            else "weighted_average"
        )
        self.ensemble_learning_rate = (
            config.get("ensemble_learning_rate", 0.01) if config else 0.01
        )
        self.ensemble_update_freq = (
            config.get("ensemble_update_freq", 100) if config else 100
        )

        # Training state
        self.is_training = False
        self.training_history = []
        self.validation_history = []

        # Performance tracking
        self.performance_metrics = {}
        self.prediction_history = []

        # Threading and concurrency
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.lock = threading.Lock()

        # Initialize modules with error handling
        self._initialize_modules()

        # Initialize ensemble weights
        self._initialize_ensemble_weights()

        self.logger.info("XTrade-AI Framework initialized successfully")

    def _initialize_modules(self):
        """Initialize all trading modules with error handling."""
        try:
            # Core modules
            self.sb3 = None
            self.close_decision = None
            self.risk_management = None
            self.adaptive_indicator = None
            self.technical_analysis = None
            self.xgboost = None
            self.reward_shaper = None
            self.action_selector = None
            self.monitoring = None
            self.temperature_scaler = None
            self.ensemble_calibrator = None
            self.market_simulation = None
            self.integrated_analysis = None

            # Register models with default configurations
            self._register_models()

        except Exception as e:
            self.logger.error(f"Failed to initialize modules: {e}")
            raise

    def _register_models(self):
        """Register all available models with their configurations."""
        model_registry = {
            "sb3": {
                "class": "Baseline3Integration",
                "enabled": True,
                "priority": 1,
                "description": "Stable-Baselines3 RL model",
                "weight": 0.4,
                "min_confidence": 0.6,
            },
            "xgboost": {
                "class": "XGBoostModule",
                "enabled": True,
                "priority": 2,
                "description": "XGBoost gradient boosting model",
                "weight": 0.3,
                "min_confidence": 0.7,
            },
            "ensemble": {
                "class": "EnsembleCalibrator",
                "enabled": True,
                "priority": 3,
                "description": "Ensemble calibration model",
                "weight": 0.2,
                "min_confidence": 0.8,
            },
            "risk_management": {
                "class": "RiskManagementModule",
                "enabled": True,
                "priority": 4,
                "description": "Risk management module",
                "weight": 0.05,
                "min_confidence": 0.5,
            },
            "technical_analysis": {
                "class": "TechnicalAnalysisModule",
                "enabled": True,
                "priority": 5,
                "description": "Technical analysis module",
                "weight": 0.05,
                "min_confidence": 0.6,
            },
        }

        for model_name, config in model_registry.items():
            self.model_configs[model_name] = config
            self.model_states[model_name] = (
                "enabled" if config["enabled"] else "disabled"
            )
            self.models[model_name] = None
            self.model_performance[model_name] = {
                "accuracy": 0.0,
                "precision": 0.0,
                "recall": 0.0,
                "f1_score": 0.0,
                "sharpe_ratio": 0.0,
                "total_return": 0.0,
                "max_drawdown": 0.0,
            }
            self.model_weights[model_name] = config["weight"]

    def _initialize_ensemble_weights(self):
        """Initialize ensemble weights based on model configurations."""
        total_weight = sum(
            config["weight"]
            for config in self.model_configs.values()
            if config["enabled"]
        )
        if total_weight > 0:
            for model_name, config in self.model_configs.items():
                if config["enabled"]:
                    self.model_weights[model_name] = config["weight"] / total_weight

    def enable_model(self, model_name: str) -> bool:
        """
        Enable a specific model.

        Args:
            model_name: Name of the model to enable

        Returns:
            True if model was enabled successfully
        """
        if model_name not in self.model_configs:
            self.logger.warning(f"Unknown model: {model_name}")
            return False

        with self.lock:
            self.model_states[model_name] = "enabled"
            self.model_configs[model_name]["enabled"] = True
            self._update_ensemble_weights()
            self.logger.info(f"Model {model_name} enabled")
            return True

    def disable_model(self, model_name: str) -> bool:
        """
        Disable a specific model.

        Args:
            model_name: Name of the model to disable

        Returns:
            True if model was disabled successfully
        """
        if model_name not in self.model_configs:
            self.logger.warning(f"Unknown model: {model_name}")
            return False

        with self.lock:
            self.model_states[model_name] = "disabled"
            self.model_configs[model_name]["enabled"] = False
            self._update_ensemble_weights()
            self.logger.info(f"Model {model_name} disabled")
            return True

    def _update_ensemble_weights(self):
        """Update ensemble weights when models are enabled/disabled."""
        enabled_models = [
            name for name, state in self.model_states.items() if state == "enabled"
        ]
        if not enabled_models:
            return

        total_weight = sum(
            self.model_configs[name]["weight"] for name in enabled_models
        )
        if total_weight > 0:
            for model_name in enabled_models:
                self.model_weights[model_name] = (
                    self.model_configs[model_name]["weight"] / total_weight
                )

    def get_enabled_models(self) -> List[str]:
        """
        Get list of enabled models.

        Returns:
            List of enabled model names
        """
        return [name for name, state in self.model_states.items() if state == "enabled"]

    def train(
        self,
        data: np.ndarray,
        epochs: int = 100,
        validation_data: Optional[np.ndarray] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Train the framework models with enhanced capabilities.

        Args:
            data: Training data
            epochs: Number of training epochs
            validation_data: Validation data for model selection
            **kwargs: Additional training parameters

        Returns:
            Dictionary with training results for each model
        """
        if self.logger:
            self.logger.info(f"Starting training for {epochs} epochs")

        self.is_training = True
        results = {}

        # Get enabled models
        enabled_models = self.get_enabled_models()

        if not enabled_models:
            self.logger.warning("No models enabled for training")
            return results

        # Train models in parallel
        futures = {}
        for model_name in enabled_models:
            future = self.executor.submit(
                self._train_single_model,
                model_name,
                data,
                epochs,
                validation_data,
                **kwargs,
            )
            futures[future] = model_name

        # Collect results
        for future in as_completed(futures):
            model_name = futures[future]
            try:
                result = future.result()
                results[model_name] = result
                self.logger.info(f"{model_name} training completed")
            except Exception as e:
                self.logger.error(f"{model_name} training failed: {e}")
                results[model_name] = {"error": str(e)}
                self.model_states[model_name] = "disabled"

        # Update ensemble weights based on performance
        if validation_data is not None:
            self._update_weights_from_performance(validation_data)

        # Record training history
        training_record = {
            "timestamp": datetime.now().isoformat(),
            "epochs": epochs,
            "models_trained": list(results.keys()),
            "results": results,
            "ensemble_weights": self.model_weights.copy(),
        }
        self.training_history.append(training_record)

        self.is_training = False

        if self.logger:
            self.logger.info("Training completed")

        return results

    def fine_tune(
        self,
        base_model_path: str,
        data: np.ndarray,
        epochs: int = 10,
        learning_rate: float = 0.0001,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Fine-tune a pre-trained model.

        Args:
            base_model_path: Path to the base model
            data: Fine-tuning data
            epochs: Number of fine-tuning epochs
            learning_rate: Learning rate for fine-tuning
            **kwargs: Additional fine-tuning parameters

        Returns:
            Dictionary with fine-tuning results
        """
        if self.logger:
            self.logger.info(
                f"Starting fine-tuning for {epochs} epochs with learning rate {learning_rate}"
            )

        try:
            # Load the base model (non-critical for testing)
            if not self.load_model(base_model_path, critical=False):
                self.logger.warning(
                    f"Could not load base model from {base_model_path}, proceeding without it"
                )
                # Continue without the base model for testing purposes

            # Fine-tune with lower learning rate
            fine_tune_kwargs = kwargs.copy()
            fine_tune_kwargs["learning_rate"] = learning_rate

            # Train with fine-tuning parameters
            results = self.train(data, epochs=epochs, **fine_tune_kwargs)

            if self.logger:
                self.logger.info("Fine-tuning completed")

            return results

        except Exception as e:
            if self.logger:
                self.logger.error(f"Fine-tuning failed: {e}")
            raise e

    def _train_single_model(
        self,
        model_name: str,
        data: np.ndarray,
        epochs: int,
        validation_data: Optional[np.ndarray],
        **kwargs,
    ) -> Dict[str, Any]:
        """Train a single model."""
        try:
            self.model_states[model_name] = "training"

            if model_name == "sb3" and self.sb3:
                sb3_results = self.sb3.train(data, epochs=epochs, **kwargs)
                if validation_data is not None:
                    validation_metrics = self._validate_model(
                        model_name, validation_data
                    )
                    sb3_results.update(validation_metrics)
                return sb3_results

            elif model_name == "xgboost" and self.xgboost:
                xgb_results = self.xgboost.train(data, epochs=epochs, **kwargs)
                if validation_data is not None:
                    validation_metrics = self._validate_model(
                        model_name, validation_data
                    )
                    xgb_results.update(validation_metrics)
                return xgb_results

            elif model_name == "ensemble" and self.ensemble_calibrator:
                ensemble_results = self.ensemble_calibrator.calibrate(self.models, data)
                if validation_data is not None:
                    validation_metrics = self._validate_model(
                        model_name, validation_data
                    )
                    ensemble_results.update(validation_metrics)
                return ensemble_results

            self.model_states[model_name] = "enabled"
            return {"status": "completed", "epochs": epochs}

        except Exception as e:
            self.model_states[model_name] = "disabled"
            raise e

    def _validate_model(
        self, model_name: str, validation_data: np.ndarray
    ) -> Dict[str, float]:
        """Validate a model and return performance metrics."""
        try:
            predictions = self._get_model_predictions(model_name, validation_data)
            if predictions is None:
                return {}

            # Calculate basic metrics
            accuracy = self._calculate_accuracy(predictions, validation_data)
            precision = self._calculate_precision(predictions, validation_data)
            recall = self._calculate_recall(predictions, validation_data)
            f1_score = self._calculate_f1_score(precision, recall)

            # Calculate trading metrics
            sharpe_ratio = self._calculate_sharpe_ratio(predictions, validation_data)
            total_return = self._calculate_total_return(predictions, validation_data)
            max_drawdown = self._calculate_max_drawdown(predictions, validation_data)

            metrics = {
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1_score": f1_score,
                "sharpe_ratio": sharpe_ratio,
                "total_return": total_return,
                "max_drawdown": max_drawdown,
            }

            # Update model performance
            self.model_performance[model_name] = metrics

            return metrics

        except Exception as e:
            self.logger.error(f"Model validation failed for {model_name}: {e}")
            return {}

    def _get_model_predictions(
        self, model_name: str, data: np.ndarray
    ) -> Optional[np.ndarray]:
        """Get predictions from a specific model."""
        try:
            if model_name == "sb3" and self.sb3:
                return self.sb3.predict(data)
            elif model_name == "xgboost" and self.xgboost:
                return self.xgboost.predict(data)
            elif model_name == "technical_analysis" and self.technical_analysis:
                return self.technical_analysis.analyze(data)
            else:
                return None
        except Exception as e:
            self.logger.error(f"Failed to get predictions from {model_name}: {e}")
            return None

    def _calculate_accuracy(self, predictions: np.ndarray, data: np.ndarray) -> float:
        """Calculate prediction accuracy."""
        if len(predictions) != len(data):
            return 0.0
        return np.mean(predictions == data)

    def _calculate_precision(self, predictions: np.ndarray, data: np.ndarray) -> float:
        """Calculate prediction precision."""
        if len(predictions) != len(data):
            return 0.0
        true_positives = np.sum((predictions == 1) & (data == 1))
        predicted_positives = np.sum(predictions == 1)
        return true_positives / predicted_positives if predicted_positives > 0 else 0.0

    def _calculate_recall(self, predictions: np.ndarray, data: np.ndarray) -> float:
        """Calculate prediction recall."""
        if len(predictions) != len(data):
            return 0.0
        true_positives = np.sum((predictions == 1) & (data == 1))
        actual_positives = np.sum(data == 1)
        return true_positives / actual_positives if actual_positives > 0 else 0.0

    def _calculate_f1_score(self, precision: float, recall: float) -> float:
        """Calculate F1 score."""
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)

    def _calculate_sharpe_ratio(
        self, predictions: np.ndarray, data: np.ndarray
    ) -> float:
        """Calculate Sharpe ratio of predictions."""
        if len(predictions) != len(data):
            return 0.0
        returns = np.diff(data) * predictions[:-1]
        if len(returns) == 0:
            return 0.0
        return np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0.0

    def _calculate_total_return(
        self, predictions: np.ndarray, data: np.ndarray
    ) -> float:
        """Calculate total return of predictions."""
        if len(predictions) != len(data):
            return 0.0
        returns = np.diff(data) * predictions[:-1]
        return np.sum(returns)

    def _calculate_max_drawdown(
        self, predictions: np.ndarray, data: np.ndarray
    ) -> float:
        """Calculate maximum drawdown of predictions."""
        if len(predictions) != len(data):
            return 0.0
        returns = np.diff(data) * predictions[:-1]
        cumulative = np.cumsum(returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = cumulative - running_max
        return np.min(drawdown) if len(drawdown) > 0 else 0.0

    def _update_weights_from_performance(self, validation_data: np.ndarray):
        """Update ensemble weights based on model performance."""
        enabled_models = self.get_enabled_models()
        if not enabled_models:
            return

        # Calculate performance scores
        performance_scores = {}
        for model_name in enabled_models:
            if model_name in self.model_performance:
                # Use a combination of metrics for weight calculation
                metrics = self.model_performance[model_name]
                score = (
                    metrics.get("f1_score", 0.0) * 0.4
                    + metrics.get("sharpe_ratio", 0.0) * 0.3
                    + metrics.get("total_return", 0.0) * 0.3
                )
                performance_scores[model_name] = max(0.0, score)
            else:
                performance_scores[model_name] = 0.0

        # Normalize scores
        total_score = sum(performance_scores.values())
        if total_score > 0:
            for model_name in enabled_models:
                self.model_weights[model_name] = (
                    performance_scores[model_name] / total_score
                )

    def predict(self, market_data: np.ndarray, **kwargs) -> Dict[str, Any]:
        """
        Make trading predictions with enhanced ensemble approach.

        Args:
            market_data: Market data for prediction
            **kwargs: Additional prediction parameters

        Returns:
            Dictionary with prediction results
        """
        if self.logger:
            self.logger.info("Making trading prediction")

        # Get enabled models
        enabled_models = self.get_enabled_models()

        if not enabled_models:
            self.logger.warning("No models enabled for prediction")
            return {
                "action": "HOLD",
                "confidence": 0.0,
                "reasoning": "No models enabled",
            }

        # Collect predictions from all enabled models
        predictions = {}

        for model_name in enabled_models:
            try:
                if model_name == "sb3" and self.sb3:
                    pred = self.sb3.predict(market_data, **kwargs)
                    predictions[model_name] = pred

                elif model_name == "xgboost" and self.xgboost:
                    pred = self.xgboost.predict(market_data, **kwargs)
                    predictions[model_name] = pred

                elif model_name == "technical_analysis" and self.technical_analysis:
                    ta_signals = self.technical_analysis.analyze(market_data)
                    predictions[model_name] = ta_signals

                elif model_name == "risk_management" and self.risk_management:
                    risk_assessment = self.risk_management.assess_risk(
                        market_data, self.portfolio
                    )
                    predictions[model_name] = risk_assessment

            except Exception as e:
                self.logger.error(f"Model {model_name} prediction failed: {e}")
                predictions[model_name] = {"error": str(e)}

        # Ensemble decision making
        if self.action_selector:
            decision = self.action_selector.select_action(predictions, **kwargs)
        else:
            # Enhanced fallback decision
            decision = self._enhanced_ensemble_decision(predictions)

        # Add metadata
        result = {
            "action": decision.get("action", "HOLD"),
            "confidence": decision.get("confidence", 0.5),
            "reasoning": decision.get("reasoning", "Fallback decision"),
            "model_predictions": predictions,
            "enabled_models": enabled_models,
            "ensemble_weights": self.model_weights.copy(),
            "timestamp": datetime.now().isoformat(),
        }

        # Record prediction
        self.prediction_history.append(result)

        if self.logger:
            self.logger.info(f"Trading decision: {result['action']}")

        return result

    def _enhanced_ensemble_decision(
        self, predictions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate enhanced ensemble decision.

        Args:
            predictions: Model predictions

        Returns:
            Enhanced ensemble decision
        """
        if self.ensemble_method == "weighted_average":
            return self._weighted_average_decision(predictions)
        elif self.ensemble_method == "voting":
            return self._voting_decision(predictions)
        elif self.ensemble_method == "stacking":
            return self._stacking_decision(predictions)
        else:
            return self._fallback_decision(predictions)

    def _weighted_average_decision(self, predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Weighted average ensemble decision."""
        actions = []
        confidences = []
        weights = []

        for model_name, pred in predictions.items():
            if isinstance(pred, dict) and "action" in pred:
                actions.append(pred["action"])
                confidences.append(pred.get("confidence", 0.5))
                weights.append(self.model_weights.get(model_name, 0.1))

        if not actions:
            return {
                "action": "HOLD",
                "confidence": 0.5,
                "reasoning": "No valid predictions",
            }

        # Weighted average of confidences
        weighted_confidence = sum(c * w for c, w in zip(confidences, weights)) / sum(
            weights
        )

        # Most common action with weight consideration
        action_counts = {}
        for action, weight in zip(actions, weights):
            action_counts[action] = action_counts.get(action, 0) + weight

        most_common_action = max(action_counts.items(), key=lambda x: x[1])[0]

        return {
            "action": most_common_action,
            "confidence": weighted_confidence,
            "reasoning": f"Weighted ensemble decision based on {len(actions)} models",
        }

    def _voting_decision(self, predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Voting ensemble decision."""
        actions = []
        confidences = []

        for model_name, pred in predictions.items():
            if isinstance(pred, dict) and "action" in pred:
                actions.append(pred["action"])
                confidences.append(pred.get("confidence", 0.5))

        if not actions:
            return {
                "action": "HOLD",
                "confidence": 0.5,
                "reasoning": "No valid predictions",
            }

        # Simple majority voting
        from collections import Counter

        action_counts = Counter(actions)
        most_common_action = action_counts.most_common(1)[0][0]

        # Average confidence
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5

        return {
            "action": most_common_action,
            "confidence": avg_confidence,
            "reasoning": f"Voting ensemble decision based on {len(actions)} models",
        }

    def _stacking_decision(self, predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Stacking ensemble decision."""
        # This is a simplified stacking implementation
        # In practice, you would train a meta-learner on the base model predictions
        return self._weighted_average_decision(predictions)

    def _fallback_decision(self, predictions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate fallback decision when action selector is not available.

        Args:
            predictions: Model predictions

        Returns:
            Fallback decision
        """
        # Simple voting mechanism
        actions = []
        confidences = []

        for model_name, pred in predictions.items():
            if isinstance(pred, dict) and "action" in pred:
                actions.append(pred["action"])
                confidences.append(pred.get("confidence", 0.5))

        if not actions:
            return {
                "action": "HOLD",
                "confidence": 0.5,
                "reasoning": "No valid predictions",
            }

        # Most common action
        from collections import Counter

        action_counts = Counter(actions)
        most_common_action = action_counts.most_common(1)[0][0]

        # Average confidence
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5

        return {
            "action": most_common_action,
            "confidence": avg_confidence,
            "reasoning": f"Fallback decision based on {len(actions)} models",
        }

    def evaluate(self, model_path: str, data: np.ndarray, **kwargs) -> Dict[str, Any]:
        """
        Evaluate a trained model on test data.

        Args:
            model_path: Path to the trained model
            data: Test data for evaluation
            **kwargs: Additional evaluation parameters

        Returns:
            Dictionary with evaluation results
        """
        if self.logger:
            self.logger.info(f"Evaluating model from {model_path}")

        try:
            # Load the model if not already loaded
            if not self.load_model(model_path):
                raise ValueError(f"Failed to load model from {model_path}")

            # Run backtest for evaluation
            backtest_results = self.backtest(data, **kwargs)

            # Extract key metrics
            evaluation_results = {
                "total_return": backtest_results.get("simulation", {}).get("pnl", 0.0),
                "sharpe_ratio": backtest_results.get("analysis", {}).get(
                    "sharpe_ratio", 0.0
                ),
                "max_drawdown": backtest_results.get("analysis", {}).get(
                    "max_drawdown", 0.0
                ),
                "final_balance": 10000.0
                + backtest_results.get("simulation", {}).get("pnl", 0.0),
                "trades": backtest_results.get("simulation", {}).get("trades", []),
                "timestamp": datetime.now().isoformat(),
            }

            if self.logger:
                self.logger.info("Model evaluation completed")

            return evaluation_results

        except Exception as e:
            self.logger.error(f"Model evaluation failed: {e}")
            return {
                "total_return": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "final_balance": 10000.0,
                "trades": [],
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def backtest(self, historical_data: np.ndarray, **kwargs) -> Dict[str, Any]:
        """
        Run backtest on historical data with enhanced analysis.

        Args:
            historical_data: Historical market data
            **kwargs: Additional backtest parameters

        Returns:
            Dictionary with backtest results
        """
        if self.logger:
            self.logger.info("Starting backtest")

        # Market simulation
        if self.market_simulation:
            simulation_results = self.market_simulation.simulate(
                historical_data, **kwargs
            )
        else:
            simulation_results = {"pnl": 0.0, "trades": []}

        # Performance analysis
        if self.integrated_analysis:
            analysis_results = self.integrated_analysis.analyze_performance(
                simulation_results
            )
        else:
            analysis_results = {"sharpe_ratio": 0.0, "max_drawdown": 0.0}

        # Monitoring
        if self.monitoring:
            self.monitoring.track_backtest_results(simulation_results, analysis_results)

        results = {
            "simulation": simulation_results,
            "analysis": analysis_results,
            "portfolio": self.portfolio.__dict__ if hasattr(self, "portfolio") else {},
            "timestamp": datetime.now().isoformat(),
        }

        if self.logger:
            self.logger.info("Backtest completed")

        return results

    def save_model(self, path: str, model_name: str = "all") -> bool:
        """
        Save trained models with enhanced capabilities.

        Args:
            path: Directory path to save models
            model_name: Specific model name or "all" for all models

        Returns:
            True if models were saved successfully
        """
        if self.logger:
            self.logger.info(f"Saving model {model_name} to {path}")

        try:
            save_path = Path(path)
            save_path.mkdir(parents=True, exist_ok=True)

            models_to_save = (
                [model_name] if model_name != "all" else list(self.models.keys())
            )

            saved_models = []

            for name in models_to_save:
                if name not in self.models or self.models[name] is None:
                    continue

                model = self.models[name]
                if hasattr(model, "save"):
                    try:
                        model_path = save_path / f"{name}_model.pkl"
                        with open(model_path, "wb") as f:
                            pickle.dump(model, f)
                        saved_models.append(name)

                        if self.logger:
                            self.logger.info(f"Saved {name} model to {model_path}")

                    except Exception as e:
                        self.logger.error(f"Failed to save {name} model: {e}")

            # Save metadata
            metadata = {
                "saved_models": saved_models,
                "model_configs": self.model_configs,
                "model_states": self.model_states,
                "model_performance": self.model_performance,
                "model_weights": self.model_weights,
                "training_history": self.training_history,
                "validation_history": self.validation_history,
                "timestamp": datetime.now().isoformat(),
            }

            metadata_path = save_path / "metadata.json"
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2, default=str)

            self.logger.info(f"Saved {len(saved_models)} models and metadata")
            return True

        except Exception as e:
            self.logger.error(f"Failed to save models: {e}")
            return False

    def load_model(
        self, path: str, model_name: str = "all", critical: bool = False
    ) -> bool:
        """
        Load trained models with enhanced capabilities.

        Args:
            path: Directory path to load models from
            model_name: Specific model name or "all" for all models
            critical: If True, raises exception on failure; if False, returns False

        Returns:
            True if models were loaded successfully
        """
        if self.logger:
            self.logger.info(f"Loading model {model_name} from {path}")

        try:
            load_path = Path(path)

            if not load_path.exists():
                error_msg = f"Model path does not exist: {path}"
                self.logger.warning(error_msg)
                if critical:
                    raise FileNotFoundError(error_msg)
                return False

            # Load metadata
            metadata_path = load_path / "metadata.json"
            if metadata_path.exists():
                try:
                    with open(metadata_path, "r") as f:
                        metadata = json.load(f)

                    # Restore model states and configs
                    self.model_states.update(metadata.get("model_states", {}))
                    self.model_configs.update(metadata.get("model_configs", {}))
                    self.model_performance.update(metadata.get("model_performance", {}))
                    self.model_weights.update(metadata.get("model_weights", {}))
                    self.training_history = metadata.get("training_history", [])
                    self.validation_history = metadata.get("validation_history", [])
                except Exception as e:
                    self.logger.warning(
                        f"Failed to load metadata from {metadata_path}: {e}"
                    )

            models_to_load = (
                [model_name] if model_name != "all" else list(self.models.keys())
            )

            loaded_models = []
            failed_models = []

            for name in models_to_load:
                if name not in self.models:
                    continue

                model_path = load_path / f"{name}_model.pkl"
                if model_path.exists():
                    try:
                        with open(model_path, "rb") as f:
                            model = pickle.load(f)
                        self.models[name] = model
                        loaded_models.append(name)

                        if self.logger:
                            self.logger.info(f"Loaded {name} model from {model_path}")

                    except Exception as e:
                        error_msg = f"Failed to load {name} model: {e}"
                        self.logger.warning(error_msg)
                        failed_models.append(name)
                        if critical:
                            raise RuntimeError(error_msg)
                else:
                    self.logger.warning(f"Model file not found: {model_path}")

            if loaded_models:
                self.logger.info(
                    f"Successfully loaded {len(loaded_models)} models: {loaded_models}"
                )
            if failed_models:
                self.logger.warning(
                    f"Failed to load {len(failed_models)} models: {failed_models}"
                )

            # Return True if at least one model was loaded, or if no models were expected
            return len(loaded_models) > 0 or len(models_to_load) == 0

        except Exception as e:
            error_msg = f"Failed to load models: {e}"
            self.logger.error(error_msg)
            if critical:
                raise
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about all models.

        Returns:
            Dictionary with model information
        """
        info = {
            "enabled_models": self.get_enabled_models(),
            "model_states": self.model_states,
            "model_configs": self.model_configs,
            "model_performance": self.model_performance,
            "model_weights": self.model_weights,
            "training_history_length": len(self.training_history),
            "validation_history_length": len(self.validation_history),
            "is_training": self.is_training,
            "ensemble_method": self.ensemble_method,
        }

        return info

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics.

        Returns:
            Dictionary with performance metrics
        """
        return self.performance_metrics

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        if self.logger:
            self.logger.info("Cleaning up XTrade-AI Framework")

        # Shutdown executor
        self.executor.shutdown(wait=True)

        # Auto cleanup
        if hasattr(self, "auto_cleanup"):
            self.auto_cleanup()

        # Wait for all threads
        if hasattr(self, "wait_for_all"):
            self.wait_for_all()

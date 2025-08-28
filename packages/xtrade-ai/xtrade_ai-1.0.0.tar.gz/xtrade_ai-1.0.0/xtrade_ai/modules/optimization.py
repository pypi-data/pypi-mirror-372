import itertools
import random
from typing import Any, Callable, Dict, List, Optional

import numpy as np

try:
    from ..config import XTradeAIConfig
    from ..utils.logger import get_logger
except ImportError:
    from config import XTradeAIConfig
    from utils.logger import get_logger


class OptimizationModule:
    """Hyperparameter optimization module for XTrade-AI Framework."""

    def __init__(self, config: Optional[XTradeAIConfig] = None):
        self.config = config or XTradeAIConfig()
        self.logger = get_logger(__name__)
        self.optimization_history: List[Dict[str, Any]] = []

    def grid_search(
        self, space: Dict[str, List[Any]], evaluator: Callable[[Dict[str, Any]], float]
    ) -> Dict[str, Any]:
        """Perform grid search optimization."""
        self.logger.info(f"Starting grid search with space: {list(space.keys())}")
        result = grid_search(space, evaluator)
        self.optimization_history.append(
            {"method": "grid_search", "space": space, "result": result}
        )
        return result

    def random_search(
        self,
        space: Dict[str, List[Any]],
        evaluator: Callable[[Dict[str, Any]], float],
        n_trials: int = 20,
    ) -> Dict[str, Any]:
        """Perform random search optimization."""
        self.logger.info(f"Starting random search with {n_trials} trials")
        result = random_search(space, evaluator, n_trials)
        self.optimization_history.append(
            {
                "method": "random_search",
                "space": space,
                "n_trials": n_trials,
                "result": result,
            }
        )
        return result

    def optimize_hyperparameters(
        self,
        param_space: Dict[str, List[Any]],
        objective_function: Callable[[Dict[str, Any]], float],
        method: str = "grid_search",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Optimize hyperparameters using specified method.

        Args:
            param_space: Dictionary of parameter names to lists of possible values
            objective_function: Function that takes parameters and returns score
            method: Optimization method ('grid_search' or 'random_search')
            **kwargs: Additional arguments for the optimization method

        Returns:
            Dictionary with best configuration and score
        """
        if method == "grid_search":
            return self.grid_search(param_space, objective_function)
        elif method == "random_search":
            n_trials = kwargs.get("n_trials", 20)
            return self.random_search(param_space, objective_function, n_trials)
        else:
            raise ValueError(f"Unsupported optimization method: {method}")

    def get_optimization_history(self) -> List[Dict[str, Any]]:
        """Get optimization history."""
        return self.optimization_history.copy()


def grid_search(
    space: Dict[str, List[Any]], evaluator: Callable[[Dict[str, Any]], float]
) -> Dict[str, Any]:
    best_cfg = None
    best_score = float("-inf")
    keys = list(space.keys())
    for values in itertools.product(*[space[k] for k in keys]):
        cfg = dict(zip(keys, values))
        score = float(evaluator(cfg))
        if score > best_score:
            best_score, best_cfg = score, cfg
    return {"best_config": best_cfg, "score": best_score}


def random_search(
    space: Dict[str, List[Any]],
    evaluator: Callable[[Dict[str, Any]], float],
    n_trials: int = 20,
) -> Dict[str, Any]:
    best_cfg = None
    best_score = float("-inf")
    keys = list(space.keys())
    for _ in range(n_trials):
        cfg = {k: random.choice(space[k]) for k in keys}
        score = float(evaluator(cfg))
        if score > best_score:
            best_score, best_cfg = score, cfg
    return {"best_config": best_cfg, "score": best_score}

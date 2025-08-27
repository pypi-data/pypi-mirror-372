from typing import List, Optional

import numpy as np

try:
    from ..config import XTradeAIConfig
    from ..utils.logger import get_logger
except ImportError:
    from config import XTradeAIConfig
    from utils.logger import get_logger

try:
    import xgboost as xgb

    xgb_error = None
except Exception as e:
    xgb = None
    xgb_error = e


class XGBoostModule:
    """XGBoost-based feature selector and auxiliary classifier."""

    def __init__(
        self, config: Optional[XTradeAIConfig] = None, top_k: Optional[int] = None
    ):
        self.config = config or XTradeAIConfig()
        self.top_k = top_k or self.config.model.xgb_top_k_features
        self.logger = get_logger(__name__)
        self.model = None
        self.selected_indices: Optional[List[int]] = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        if xgb is None:
            self.logger.warning(f"xgboost not available: {xgb_error}")
            return
        self.model = xgb.XGBClassifier(
            n_estimators=self.config.model.xgb_n_estimators,
            max_depth=self.config.model.xgb_max_depth,
            learning_rate=self.config.model.xgb_learning_rate,
            tree_method="gpu_hist" if self._has_gpu() else "hist",
        )
        self.model.fit(X, y)
        # Feature importance-based selection
        importance = self.model.feature_importances_
        self.selected_indices = list(np.argsort(importance)[-self.top_k :])

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if self.model is None:
            return np.full((X.shape[0], 2), 0.5, dtype=np.float32)
        if self.selected_indices is not None:
            X = X[:, self.selected_indices]
        return self.model.predict_proba(X)

    def _has_gpu(self) -> bool:
        try:
            import torch

            return torch.cuda.is_available()
        except Exception:
            return False

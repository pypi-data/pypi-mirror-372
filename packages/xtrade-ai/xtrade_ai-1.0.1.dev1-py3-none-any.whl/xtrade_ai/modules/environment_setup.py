from typing import Any, Dict, Optional

import numpy as np

try:
    from ..base_environment import XTradeEnvironment
    from ..config import XTradeAIConfig
    from ..data_preprocessor import DataPreprocessor
    from ..modules.monitoring import MonitoringModule
except ImportError:
    from base_environment import XTradeEnvironment
    from data_preprocessor import DataPreprocessor
    from modules.monitoring import MonitoringModule

    from ..config import XTradeAIConfig


def build_env(
    config: Optional[XTradeAIConfig],
    ohlcv: np.ndarray,
    indicators: np.ndarray,
    session_type: str = "training",
) -> XTradeEnvironment:
    cfg = config or XTradeAIConfig()
    pre = DataPreprocessor(cfg)
    pre.fit(ohlcv, indicators) if session_type == "training" else None
    d = pre.transform(ohlcv, indicators)
    mon = MonitoringModule()
    mon.start_session(
        session_type=session_type, metadata={"builder": "environment_setup"}
    )
    return XTradeEnvironment(cfg, d["ohlcv"], d["indicators"], monitor=mon)

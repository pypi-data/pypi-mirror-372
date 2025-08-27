from typing import Any, Dict, List, Tuple

import numpy as np


class MarketSimulation:
    """Generate synthetic OHLCV datasets across regimes for meta-learning."""

    def __init__(self, seed: int = 42):
        self.rng = np.random.default_rng(seed)

    def simulate(
        self,
        base_ohlcv: np.ndarray,
        regimes: List[str],
        multiplier: int = 1,
        drift_range: Tuple[float, float] = (0.0005, 0.002),
        vol_multipliers: List[float] = [0.5, 1.0, 1.5],
    ) -> Dict[str, List[np.ndarray]]:
        results: Dict[str, List[np.ndarray]] = {r: [] for r in regimes}
        for regime in regimes:
            for _ in range(max(1, multiplier)):
                sim = self._simulate_regime(
                    base_ohlcv, regime, drift_range, vol_multipliers
                )
                results[regime].append(sim)
        return results

    def _simulate_regime(
        self,
        base_ohlcv: np.ndarray,
        regime: str,
        drift_range: Tuple[float, float],
        vol_multipliers: List[float],
    ) -> np.ndarray:
        N = base_ohlcv.shape[0]
        close = base_ohlcv[:, 3].astype(np.float32)
        vol = np.std(np.diff(close)) + 1e-6
        drift = float(self.rng.uniform(*drift_range))
        vol_mult = float(self.rng.choice(vol_multipliers))
        noise = self.rng.normal(0, vol * vol_mult, size=N).astype(np.float32)
        trend = np.linspace(0, drift * N, N).astype(np.float32)
        if regime == "trending":
            series = close[0] + trend + noise
        elif regime == "ranging":
            series = close[0] + self._mean_reverting(noise)
        elif regime == "volatile":
            noise = self.rng.normal(0, vol * vol_mult * 2.0, size=N).astype(np.float32)
            series = close[0] + noise
        elif regime == "quiet":
            noise = self.rng.normal(0, vol * 0.3, size=N).astype(np.float32)
            series = close[0] + noise
        else:
            series = close
        return self._series_to_ohlcv(series)

    def _mean_reverting(self, noise: np.ndarray, alpha: float = 0.9) -> np.ndarray:
        mr = np.zeros_like(noise)
        for i in range(1, len(noise)):
            mr[i] = alpha * mr[i - 1] + noise[i]
        return mr

    def _series_to_ohlcv(self, close: np.ndarray) -> np.ndarray:
        N = len(close)
        high = close + np.abs(self.rng.normal(0, 0.1, N)).astype(np.float32)
        low = close - np.abs(self.rng.normal(0, 0.1, N)).astype(np.float32)
        opn = close + self.rng.normal(0, 0.05, N).astype(np.float32)
        volume = self.rng.uniform(5e5, 2e6, N).astype(np.float32)
        return np.column_stack([opn, high, low, close, volume]).astype(np.float32)

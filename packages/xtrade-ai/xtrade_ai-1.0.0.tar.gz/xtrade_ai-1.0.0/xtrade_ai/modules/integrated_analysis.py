from typing import Any, Dict

import numpy as np


class IntegratedAnalysis:
    """Provide post-run diagnostics from Monitoring export.
    - Per-action average reward
    - Reward distribution
    - Top-N losses/gains
    - Simple confusion-like matrix for buy/sell vs realized PnL sign
    """

    def __init__(self, report: Dict[str, Any]):
        self.report = report or {}
        self.steps = self.report.get("trading_steps", [])

    def per_action_stats(self) -> Dict[str, float]:
        buckets = {}
        for s in self.steps:
            a = int(s.get("action", -1))
            buckets.setdefault(a, []).append(float(s.get("reward", 0.0)))
        return {str(k): float(np.mean(v)) for k, v in buckets.items() if v}

    def reward_distribution(self) -> Dict[str, float]:
        rv = np.array(
            [float(s.get("reward", 0.0)) for s in self.steps], dtype=np.float32
        )
        if rv.size == 0:
            return {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0}
        return {
            "mean": float(rv.mean()),
            "std": float(rv.std()),
            "min": float(rv.min()),
            "max": float(rv.max()),
        }

    def top_losses(self, n: int = 10):
        return sorted(self.steps, key=lambda s: s.get("reward", 0.0))[:n]

    def top_gains(self, n: int = 10):
        return sorted(self.steps, key=lambda s: s.get("reward", 0.0), reverse=True)[:n]

    def pseudo_confusion(self) -> Dict[str, int]:
        """Approximate: buy positive vs negative next-step reward; sell likewise."""
        counts = {"buy_pos": 0, "buy_neg": 0, "sell_pos": 0, "sell_neg": 0}
        for s in self.steps:
            a = int(s.get("action", -1))
            r = float(s.get("reward", 0.0))
            if a == 0:
                if r >= 0:
                    counts["buy_pos"] += 1
                else:
                    counts["buy_neg"] += 1
            elif a == 1:
                if r >= 0:
                    counts["sell_pos"] += 1
                else:
                    counts["sell_neg"] += 1
        return counts

    def step_mean(self, key: str) -> float:
        vals = [float(s.get(key, 0.0)) for s in self.steps if key in s]
        if not vals:
            return 0.0
        return float(sum(vals) / len(vals))

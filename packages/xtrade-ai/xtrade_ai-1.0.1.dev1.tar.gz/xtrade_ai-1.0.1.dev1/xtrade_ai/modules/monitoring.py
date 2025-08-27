from typing import Any, Dict, List, Optional

try:
    from ..utils.logger import get_logger

    except_import_error = None
except ImportError as e:
    from utils.logger import get_logger

    except_import_error = e

try:
    from ..data_structures import TradingMetrics as TRM
    from ..data_structures import TrainingMetrics as TM
except ImportError:
    from data_structures import TradingMetrics as TRM
    from data_structures import TrainingMetrics as TM

try:
    import matplotlib.pyplot as plt

    _has_mpl = True
except Exception:
    _has_mpl = False

# Optional SB3 callback integration
try:
    from stable_baselines3.common.callbacks import BaseCallback

    _SB3_AVAILABLE = True
except Exception:
    BaseCallback = object  # type: ignore
    _SB3_AVAILABLE = False


class MonitoringModule:
    """Record and visualize training/trading metrics and per-module performance."""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.session_type: str = "unknown"
        self.session_meta: Dict[str, Any] = {}
        # Training metrics
        self.training_metrics: List[Dict[str, Any]] = []
        # Trading step-level metrics
        self.trading_steps: List[Dict[str, Any]] = []
        # Episode summaries
        self.episodes: List[Dict[str, Any]] = []
        # Per-module metrics
        self.module_metrics: Dict[str, List[Dict[str, Any]]] = {}
        # Aggregated performance
        self.trading_perf = TRM()
        # Equity curve for analytics
        self._equity_series: List[float] = []
        self._balance_series: List[float] = []

    def start_session(
        self, session_type: str = "training", metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        self.session_type = session_type
        self.session_meta = metadata or {}
        self.logger.info(f"Monitoring session started: {session_type}")

    def record_training_metrics(self, metrics: TM) -> None:
        self.training_metrics.append(metrics.to_dict())
        self.logger.debug(f"Training metrics: {metrics.to_dict()}")

    def record_step(
        self,
        step_idx: int,
        action: int,
        reward: float,
        balance: float,
        equity: float,
        open_positions: int,
        info: Optional[Dict[str, Any]] = None,
    ) -> None:
        entry = {
            "step": step_idx,
            "action": action,
            "reward": float(reward),
            "balance": float(balance),
            "equity": float(equity),
            "open_positions": int(open_positions),
        }
        if info:
            entry.update(info)
        self.trading_steps.append(entry)
        self._equity_series.append(float(equity))
        self._balance_series.append(float(balance))

    def record_episode(
        self, episode_idx: int, total_reward: float, total_steps: int, pnl: float
    ) -> None:
        self.episodes.append(
            {
                "episode": episode_idx,
                "total_reward": float(total_reward),
                "total_steps": int(total_steps),
                "pnl": float(pnl),
            }
        )

    def record_trade_open(
        self, position_id: str, side: str, entry_price: float, quantity: float
    ) -> None:
        self.logger.debug(
            f"Trade open: {position_id} {side} qty={quantity} @ {entry_price}"
        )

    def record_trade_close(
        self, position_id: str, exit_price: float, pnl: float, pnl_pct: float
    ) -> None:
        # Update aggregated trading performance
        self.trading_perf.update(trade_pnl=pnl)
        self.logger.debug(
            f"Trade close: {position_id} exit={exit_price} pnl={pnl} ({pnl_pct:.2%})"
        )

    def record_module_metric(self, module_name: str, metrics: Dict[str, Any]) -> None:
        if module_name not in self.module_metrics:
            self.module_metrics[module_name] = []
        self.module_metrics[module_name].append(metrics)

    def get_trading_performance(self) -> Dict[str, Any]:
        sharpe = self._compute_sharpe(self._equity_series)
        mdd = self._compute_max_drawdown(self._equity_series)
        perf = self.trading_perf.to_dict()
        perf.update({"sharpe_ratio": sharpe, "max_drawdown": mdd})
        return perf

    def export_json(self) -> Dict[str, Any]:
        return {
            "session": {"type": self.session_type, **self.session_meta},
            "training_metrics": self.training_metrics,
            "trading_steps": self.trading_steps,
            "episodes": self.episodes,
            "per_module": self.module_metrics,
            "performance": self.get_trading_performance(),
        }

    def plot_equity(self):
        if not _has_mpl or not self._equity_series:
            self.logger.info("Matplotlib not available or no equity data to plot.")
            return
        plt.figure(figsize=(8, 4))
        plt.plot(self._equity_series, label="Equity")
        plt.title("Equity Curve")
        plt.legend()
        plt.tight_layout()
        plt.show()

    def plot_rewards(self):
        if not _has_mpl or not self.trading_steps:
            self.logger.info("Matplotlib not available or no rewards to plot.")
            return
        plt.figure(figsize=(8, 4))
        plt.plot([s.get("reward", 0) for s in self.trading_steps], label="Reward")
        plt.title("Step Rewards")
        plt.legend()
        plt.tight_layout()
        plt.show()

    def _compute_sharpe(self, equity_series: List[float], eps: float = 1e-12) -> float:
        if len(equity_series) < 2:
            return 0.0
        import numpy as np

        returns = np.diff(np.array(equity_series))
        mu = returns.mean()
        sigma = returns.std() + eps
        sharpe = (mu / sigma) * (len(returns) ** 0.5)
        return float(sharpe)

    def _compute_max_drawdown(self, equity_series: List[float]) -> float:
        if not equity_series:
            return 0.0
        import numpy as np

        arr = np.array(equity_series)
        roll_max = np.maximum.accumulate(arr)
        drawdown = (arr - roll_max) / (roll_max + 1e-12)
        return float(abs(drawdown.min()))

    # Optional SB3 callback generator
    def get_sb3_callback(self):
        if not _SB3_AVAILABLE:
            return None
        monitor = self

        class SB3MonitoringCallback(BaseCallback):  # type: ignore
            def __init__(self):
                super().__init__()
                self._n_calls = 0

            def _on_step(self) -> bool:
                self._n_calls += 1
                try:
                    monitor.record_module_metric(
                        "sb3", {"num_timesteps": int(self.num_timesteps)}
                    )
                except Exception:
                    pass
                return True

        return SB3MonitoringCallback()

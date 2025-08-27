"""
Performance monitoring utilities for XTrade-AI Framework.

This module provides utilities for tracking and analyzing trading performance,
including metrics calculation, visualization, and reporting.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Comprehensive trading performance metrics."""

    # Basic metrics
    total_return: float = 0.0
    annualized_return: float = 0.0
    volatility: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0

    # Risk metrics
    max_drawdown: float = 0.0
    max_drawdown_duration: int = 0
    var_95: float = 0.0  # Value at Risk 95%
    cvar_95: float = 0.0  # Conditional Value at Risk 95%
    downside_deviation: float = 0.0

    # Trading metrics
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    profit_factor: float = 0.0
    avg_trade_duration: float = 0.0

    # Additional metrics
    best_trade: float = 0.0
    worst_trade: float = 0.0
    consecutive_wins: int = 0
    consecutive_losses: int = 0
    recovery_factor: float = 0.0
    risk_reward_ratio: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_return": self.total_return,
            "annualized_return": self.annualized_return,
            "volatility": self.volatility,
            "sharpe_ratio": self.sharpe_ratio,
            "sortino_ratio": self.sortino_ratio,
            "calmar_ratio": self.calmar_ratio,
            "max_drawdown": self.max_drawdown,
            "max_drawdown_duration": self.max_drawdown_duration,
            "var_95": self.var_95,
            "cvar_95": self.cvar_95,
            "downside_deviation": self.downside_deviation,
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": self.win_rate,
            "avg_win": self.avg_win,
            "avg_loss": self.avg_loss,
            "profit_factor": self.profit_factor,
            "avg_trade_duration": self.avg_trade_duration,
            "best_trade": self.best_trade,
            "worst_trade": self.worst_trade,
            "consecutive_wins": self.consecutive_wins,
            "consecutive_losses": self.consecutive_losses,
            "recovery_factor": self.recovery_factor,
            "risk_reward_ratio": self.risk_reward_ratio,
        }


class PerformanceMonitor:
    """
    Performance monitor for tracking and analyzing trading performance.

    This class provides functionality for:
    - Real-time performance tracking
    - Comprehensive metrics calculation
    - Performance visualization
    - Performance reporting
    - Benchmark comparison
    """

    def __init__(self, initial_balance: float = 10000.0):
        """
        Initialize performance monitor.

        Args:
            initial_balance: Initial account balance
        """
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.equity_curve = []
        self.trades = []
        self.daily_returns = []
        self.metrics_history = []

        self.logger = logging.getLogger(__name__)
        self.logger.info(
            f"PerformanceMonitor initialized with balance: {initial_balance}"
        )

    def update_balance(self, balance: float, timestamp: datetime = None):
        """
        Update current balance and record equity curve.

        Args:
            balance: Current balance
            timestamp: Timestamp for the update
        """
        if timestamp is None:
            timestamp = datetime.now()

        self.current_balance = balance
        self.equity_curve.append(
            {
                "timestamp": timestamp,
                "balance": balance,
                "return": (balance - self.initial_balance) / self.initial_balance,
            }
        )

    def add_trade(self, trade: Dict[str, Any]):
        """
        Add a completed trade to the performance tracking.

        Args:
            trade: Trade information dictionary
        """
        self.trades.append(trade)

        # Calculate daily returns if we have enough data
        if len(self.equity_curve) > 1:
            daily_return = (
                self.current_balance - self.equity_curve[-2]["balance"]
            ) / self.equity_curve[-2]["balance"]
            self.daily_returns.append(daily_return)

    def calculate_metrics(self) -> PerformanceMetrics:
        """
        Calculate comprehensive performance metrics.

        Returns:
            PerformanceMetrics object
        """
        if not self.trades:
            return PerformanceMetrics()

        # Convert to DataFrame for easier calculations
        trades_df = pd.DataFrame(self.trades)
        equity_df = pd.DataFrame(self.equity_curve)

        # Basic return calculations
        total_return = (
            self.current_balance - self.initial_balance
        ) / self.initial_balance

        # Calculate annualized return
        if len(equity_df) > 1:
            start_date = equity_df.iloc[0]["timestamp"]
            end_date = equity_df.iloc[-1]["timestamp"]
            days = (end_date - start_date).days
            if days > 0:
                annualized_return = ((1 + total_return) ** (365 / days)) - 1
            else:
                annualized_return = total_return
        else:
            annualized_return = total_return

        # Volatility calculation
        if len(self.daily_returns) > 1:
            volatility = np.std(self.daily_returns) * np.sqrt(252)  # Annualized
        else:
            volatility = 0.0

        # Sharpe ratio
        if volatility > 0:
            sharpe_ratio = annualized_return / volatility
        else:
            sharpe_ratio = 0.0

        # Sortino ratio
        if len(self.daily_returns) > 1:
            downside_returns = [r for r in self.daily_returns if r < 0]
            if downside_returns:
                downside_deviation = np.std(downside_returns) * np.sqrt(252)
                if downside_deviation > 0:
                    sortino_ratio = annualized_return / downside_deviation
                else:
                    sortino_ratio = 0.0
            else:
                sortino_ratio = float("inf") if annualized_return > 0 else 0.0
        else:
            sortino_ratio = 0.0

        # Maximum drawdown
        max_drawdown, max_drawdown_duration = self._calculate_max_drawdown(equity_df)

        # Value at Risk and Conditional VaR
        if len(self.daily_returns) > 1:
            var_95 = np.percentile(self.daily_returns, 5)
            cvar_95 = np.mean([r for r in self.daily_returns if r <= var_95])
        else:
            var_95 = 0.0
            cvar_95 = 0.0

        # Trading metrics
        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df["pnl"] > 0])
        losing_trades = len(trades_df[trades_df["pnl"] < 0])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0.0

        if winning_trades > 0:
            avg_win = trades_df[trades_df["pnl"] > 0]["pnl"].mean()
        else:
            avg_win = 0.0

        if losing_trades > 0:
            avg_loss = abs(trades_df[trades_df["pnl"] < 0]["pnl"].mean())
        else:
            avg_loss = 0.0

        profit_factor = avg_win / avg_loss if avg_loss > 0 else float("inf")

        # Trade duration
        if "duration" in trades_df.columns:
            avg_trade_duration = trades_df["duration"].mean()
        else:
            avg_trade_duration = 0.0

        # Best and worst trades
        best_trade = trades_df["pnl"].max() if total_trades > 0 else 0.0
        worst_trade = trades_df["pnl"].min() if total_trades > 0 else 0.0

        # Consecutive wins/losses
        consecutive_wins, consecutive_losses = self._calculate_consecutive_trades(
            trades_df
        )

        # Calmar ratio
        calmar_ratio = (
            annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0.0
        )

        # Recovery factor
        recovery_factor = total_return / abs(max_drawdown) if max_drawdown != 0 else 0.0

        # Risk-reward ratio
        risk_reward_ratio = avg_win / avg_loss if avg_loss > 0 else 0.0

        metrics = PerformanceMetrics(
            total_return=total_return,
            annualized_return=annualized_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            max_drawdown=max_drawdown,
            max_drawdown_duration=max_drawdown_duration,
            var_95=var_95,
            cvar_95=cvar_95,
            downside_deviation=(
                downside_deviation if "downside_deviation" in locals() else 0.0
            ),
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            avg_trade_duration=avg_trade_duration,
            best_trade=best_trade,
            worst_trade=worst_trade,
            consecutive_wins=consecutive_wins,
            consecutive_losses=consecutive_losses,
            recovery_factor=recovery_factor,
            risk_reward_ratio=risk_reward_ratio,
        )

        # Store metrics history
        self.metrics_history.append(
            {"timestamp": datetime.now(), "metrics": metrics.to_dict()}
        )

        return metrics

    def _calculate_max_drawdown(self, equity_df: pd.DataFrame) -> Tuple[float, int]:
        """Calculate maximum drawdown and its duration."""
        if len(equity_df) < 2:
            return 0.0, 0

        # Calculate running maximum
        equity_df = equity_df.copy()
        equity_df["running_max"] = equity_df["balance"].expanding().max()
        equity_df["drawdown"] = (
            equity_df["balance"] - equity_df["running_max"]
        ) / equity_df["running_max"]

        max_drawdown = equity_df["drawdown"].min()

        # Calculate drawdown duration
        if max_drawdown < 0:
            peak_idx = equity_df["balance"].idxmax()
            recovery_idx = equity_df.loc[peak_idx:, "balance"].idxmax()
            if recovery_idx > peak_idx:
                max_drawdown_duration = (
                    equity_df.loc[recovery_idx, "timestamp"]
                    - equity_df.loc[peak_idx, "timestamp"]
                ).days
            else:
                max_drawdown_duration = 0
        else:
            max_drawdown_duration = 0

        return max_drawdown, max_drawdown_duration

    def _calculate_consecutive_trades(self, trades_df: pd.DataFrame) -> Tuple[int, int]:
        """Calculate consecutive wins and losses."""
        if len(trades_df) == 0:
            return 0, 0

        trades_df = trades_df.copy()
        trades_df["is_win"] = trades_df["pnl"] > 0

        # Calculate consecutive wins
        consecutive_wins = 0
        current_wins = 0
        for is_win in trades_df["is_win"]:
            if is_win:
                current_wins += 1
                consecutive_wins = max(consecutive_wins, current_wins)
            else:
                current_wins = 0

        # Calculate consecutive losses
        consecutive_losses = 0
        current_losses = 0
        for is_win in trades_df["is_win"]:
            if not is_win:
                current_losses += 1
                consecutive_losses = max(consecutive_losses, current_losses)
            else:
                current_losses = 0

        return consecutive_wins, consecutive_losses

    def plot_equity_curve(self, save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot equity curve with drawdown.

        Args:
            save_path: Path to save the plot

        Returns:
            Matplotlib figure
        """
        if not self.equity_curve:
            self.logger.warning("No equity curve data to plot")
            return None

        equity_df = pd.DataFrame(self.equity_curve)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

        # Plot equity curve
        ax1.plot(
            equity_df["timestamp"],
            equity_df["balance"],
            label="Account Balance",
            linewidth=2,
        )
        ax1.axhline(
            y=self.initial_balance,
            color="r",
            linestyle="--",
            alpha=0.7,
            label="Initial Balance",
        )
        ax1.set_ylabel("Balance ($)")
        ax1.set_title("Equity Curve")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot drawdown
        equity_df["running_max"] = equity_df["balance"].expanding().max()
        equity_df["drawdown"] = (
            (equity_df["balance"] - equity_df["running_max"])
            / equity_df["running_max"]
            * 100
        )

        ax2.fill_between(
            equity_df["timestamp"], equity_df["drawdown"], 0, alpha=0.3, color="red"
        )
        ax2.plot(
            equity_df["timestamp"], equity_df["drawdown"], color="red", linewidth=1
        )
        ax2.set_ylabel("Drawdown (%)")
        ax2.set_xlabel("Date")
        ax2.set_title("Drawdown")
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")

        return fig

    def plot_trade_analysis(self, save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot trade analysis charts.

        Args:
            save_path: Path to save the plot

        Returns:
            Matplotlib figure
        """
        if not self.trades:
            self.logger.warning("No trades data to plot")
            return None

        trades_df = pd.DataFrame(self.trades)

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

        # Trade PnL distribution
        ax1.hist(
            trades_df["pnl"], bins=30, alpha=0.7, color="skyblue", edgecolor="black"
        )
        ax1.axvline(x=0, color="red", linestyle="--", alpha=0.7)
        ax1.set_xlabel("Trade PnL ($)")
        ax1.set_ylabel("Frequency")
        ax1.set_title("Trade PnL Distribution")
        ax1.grid(True, alpha=0.3)

        # Cumulative PnL
        trades_df["cumulative_pnl"] = trades_df["pnl"].cumsum()
        ax2.plot(range(len(trades_df)), trades_df["cumulative_pnl"], linewidth=2)
        ax2.set_xlabel("Trade Number")
        ax2.set_ylabel("Cumulative PnL ($)")
        ax2.set_title("Cumulative PnL")
        ax2.grid(True, alpha=0.3)

        # Win/Loss ratio pie chart
        winning_trades = len(trades_df[trades_df["pnl"] > 0])
        losing_trades = len(trades_df[trades_df["pnl"] < 0])
        ax3.pie(
            [winning_trades, losing_trades],
            labels=["Winning", "Losing"],
            autopct="%1.1f%%",
            colors=["lightgreen", "lightcoral"],
        )
        ax3.set_title("Win/Loss Ratio")

        # Monthly returns heatmap
        if "timestamp" in trades_df.columns:
            trades_df["month"] = pd.to_datetime(trades_df["timestamp"]).dt.to_period(
                "M"
            )
            monthly_pnl = trades_df.groupby("month")["pnl"].sum()
            monthly_pnl_matrix = monthly_pnl.values.reshape(-1, 1)
            im = ax4.imshow(monthly_pnl_matrix, cmap="RdYlGn", aspect="auto")
            ax4.set_title("Monthly PnL Heatmap")
            ax4.set_xlabel("Month")
            ax4.set_ylabel("PnL")
            plt.colorbar(im, ax=ax4)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")

        return fig

    def generate_report(self, save_path: Optional[str] = None) -> str:
        """
        Generate comprehensive performance report.

        Args:
            save_path: Path to save the report

        Returns:
            Report text
        """
        metrics = self.calculate_metrics()

        report = f"""
XTrade-AI Performance Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

=== PERFORMANCE SUMMARY ===
Initial Balance: ${self.initial_balance:,.2f}
Current Balance: ${self.current_balance:,.2f}
Total Return: {metrics.total_return:.2%}
Annualized Return: {metrics.annualized_return:.2%}

=== RISK METRICS ===
Volatility: {metrics.volatility:.2%}
Sharpe Ratio: {metrics.sharpe_ratio:.2f}
Sortino Ratio: {metrics.sortino_ratio:.2f}
Calmar Ratio: {metrics.calmar_ratio:.2f}
Maximum Drawdown: {metrics.max_drawdown:.2%}
Maximum Drawdown Duration: {metrics.max_drawdown_duration} days
Value at Risk (95%): {metrics.var_95:.2%}
Conditional VaR (95%): {metrics.cvar_95:.2%}

=== TRADING METRICS ===
Total Trades: {metrics.total_trades}
Winning Trades: {metrics.winning_trades}
Losing Trades: {metrics.losing_trades}
Win Rate: {metrics.win_rate:.2%}
Average Win: ${metrics.avg_win:.2f}
Average Loss: ${metrics.avg_loss:.2f}
Profit Factor: {metrics.profit_factor:.2f}
Best Trade: ${metrics.best_trade:.2f}
Worst Trade: ${metrics.worst_trade:.2f}
Consecutive Wins: {metrics.consecutive_wins}
Consecutive Losses: {metrics.consecutive_losses}
Recovery Factor: {metrics.recovery_factor:.2f}
Risk-Reward Ratio: {metrics.risk_reward_ratio:.2f}

=== PERFORMANCE ASSESSMENT ===
"""

        # Performance assessment
        if metrics.sharpe_ratio > 1.0:
            report += "Sharpe Ratio: EXCELLENT (>1.0)\n"
        elif metrics.sharpe_ratio > 0.5:
            report += "Sharpe Ratio: GOOD (0.5-1.0)\n"
        else:
            report += "Sharpe Ratio: NEEDS IMPROVEMENT (<0.5)\n"

        if metrics.max_drawdown > -0.2:
            report += "Risk Management: GOOD (Max DD < 20%)\n"
        else:
            report += "Risk Management: NEEDS IMPROVEMENT (Max DD > 20%)\n"

        if metrics.win_rate > 0.5:
            report += "Win Rate: GOOD (>50%)\n"
        else:
            report += "Win Rate: NEEDS IMPROVEMENT (<50%)\n"

        if save_path:
            with open(save_path, "w") as f:
                f.write(report)

        return report

    def compare_with_benchmark(
        self, benchmark_returns: List[float], benchmark_name: str = "Benchmark"
    ) -> Dict[str, Any]:
        """
        Compare performance with a benchmark.

        Args:
            benchmark_returns: List of benchmark returns
            benchmark_name: Name of the benchmark

        Returns:
            Comparison metrics
        """
        if not self.daily_returns:
            return {}

        # Calculate benchmark metrics
        benchmark_total_return = (1 + np.array(benchmark_returns)).prod() - 1
        benchmark_volatility = np.std(benchmark_returns) * np.sqrt(252)
        benchmark_sharpe = (
            benchmark_total_return / benchmark_volatility
            if benchmark_volatility > 0
            else 0
        )

        # Calculate strategy metrics
        strategy_total_return = (1 + np.array(self.daily_returns)).prod() - 1
        strategy_volatility = np.std(self.daily_returns) * np.sqrt(252)
        strategy_sharpe = (
            strategy_total_return / strategy_volatility
            if strategy_volatility > 0
            else 0
        )

        # Calculate excess return and information ratio
        excess_returns = np.array(self.daily_returns) - np.array(benchmark_returns)
        excess_return = np.mean(excess_returns) * 252
        tracking_error = np.std(excess_returns) * np.sqrt(252)
        information_ratio = excess_return / tracking_error if tracking_error > 0 else 0

        # Calculate beta and alpha
        if len(benchmark_returns) > 1:
            covariance = np.cov(self.daily_returns, benchmark_returns)[0, 1]
            benchmark_variance = np.var(benchmark_returns)
            beta = covariance / benchmark_variance if benchmark_variance > 0 else 0
            alpha = strategy_total_return - (beta * benchmark_total_return)
        else:
            beta = 0
            alpha = 0

        comparison = {
            "strategy_total_return": strategy_total_return,
            "benchmark_total_return": benchmark_total_return,
            "excess_return": excess_return,
            "strategy_volatility": strategy_volatility,
            "benchmark_volatility": benchmark_volatility,
            "strategy_sharpe": strategy_sharpe,
            "benchmark_sharpe": benchmark_sharpe,
            "information_ratio": information_ratio,
            "beta": beta,
            "alpha": alpha,
            "tracking_error": tracking_error,
        }

        return comparison

    def save_data(self, file_path: str):
        """
        Save performance data to file.

        Args:
            file_path: Path to save the data
        """
        data = {
            "initial_balance": self.initial_balance,
            "current_balance": self.current_balance,
            "equity_curve": self.equity_curve,
            "trades": self.trades,
            "daily_returns": self.daily_returns,
            "metrics_history": self.metrics_history,
        }

        with open(file_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

        self.logger.info(f"Performance data saved to {file_path}")

    def load_data(self, file_path: str):
        """
        Load performance data from file.

        Args:
            file_path: Path to load the data from
        """
        with open(file_path, "r") as f:
            data = json.load(f)

        self.initial_balance = data["initial_balance"]
        self.current_balance = data["current_balance"]
        self.equity_curve = data["equity_curve"]
        self.trades = data["trades"]
        self.daily_returns = data["daily_returns"]
        self.metrics_history = data["metrics_history"]

        self.logger.info(f"Performance data loaded from {file_path}")

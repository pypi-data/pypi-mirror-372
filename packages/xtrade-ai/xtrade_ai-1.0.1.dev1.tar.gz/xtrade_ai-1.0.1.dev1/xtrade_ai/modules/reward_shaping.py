"""
XTrade-AI Reward Shaping Module

Handles reward calculation with proper transaction costs and normalization.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

import numpy as np

try:
    from ..config import XTradeAIConfig
    from ..utils.logger import get_logger
except ImportError:
    from config import XTradeAIConfig
    from utils.logger import get_logger


@dataclass
class RewardComponents:
    """Components of the reward calculation."""

    pnl: float = 0.0
    close_bonus: float = 0.0
    risk_penalty: float = 0.0
    cost_penalty: float = 0.0
    drawdown_penalty: float = 0.0
    volatility_penalty: float = 0.0
    transaction_cost: float = 0.0
    slippage_cost: float = 0.0


class RewardShaper:
    """Enhanced reward shaping with proper transaction costs and normalization."""

    def __init__(self, config: XTradeAIConfig):
        self.config = config
        self.logger = get_logger(__name__) if get_logger else None

        # Reward weights
        self.pnl_weight = config.environment.pnl_weight
        self.close_rule_weight = config.environment.close_rule_weight
        self.risk_penalty_weight = config.environment.risk_penalty_weight
        self.cost_weight = config.environment.cost_weight
        self.drawdown_penalty_weight = config.environment.drawdown_penalty_weight
        self.volatility_penalty_weight = config.environment.volatility_penalty_weight

        # Trading costs
        self.commission_rate = config.trading.commission_rate
        self.slippage = config.trading.slippage

        # State tracking
        self._equity_history = []
        self._max_equity = 0.0
        self._initial_equity = 0.0
        self._position_count_history = []
        self._volatility_window = 20

        # Normalization parameters
        self._reward_mean = 0.0
        self._reward_std = 1.0
        self._reward_count = 0

    def update_equity(self, equity: float):
        """Update equity tracking for drawdown calculation."""
        if self._initial_equity == 0:
            self._initial_equity = equity

        self._equity_history.append(equity)
        self._max_equity = max(self._max_equity, equity)

        # Keep only recent history for memory efficiency
        if len(self._equity_history) > 1000:
            self._equity_history = self._equity_history[-500:]

    def update_position_count(self, position_count: int):
        """Update position count for risk tracking."""
        self._position_count_history.append(position_count)

        # Keep only recent history
        if len(self._position_count_history) > 1000:
            self._position_count_history = self._position_count_history[-500:]

    def transaction_cost(self, notional_value: float) -> float:
        """
        Calculate transaction costs including commission and slippage.

        Args:
            notional_value: Total value of the transaction

        Returns:
            Total transaction cost
        """
        commission = notional_value * self.commission_rate
        slippage_cost = notional_value * self.slippage
        return commission + slippage_cost

    def drawdown(self) -> float:
        """Calculate current drawdown percentage."""
        if not self._equity_history or self._max_equity == 0:
            return 0.0

        current_equity = self._equity_history[-1]
        drawdown = (self._max_equity - current_equity) / self._max_equity
        return max(0.0, drawdown)

    def realized_volatility(self) -> float:
        """Calculate realized volatility of equity."""
        if len(self._equity_history) < 2:
            return 0.0

        # Calculate returns
        equity_array = np.array(self._equity_history)
        returns = np.diff(equity_array) / equity_array[:-1]

        # Calculate rolling volatility
        if len(returns) >= self._volatility_window:
            recent_returns = returns[-self._volatility_window :]
            volatility = np.std(recent_returns)
        else:
            volatility = np.std(returns) if len(returns) > 0 else 0.0

        return float(volatility)

    def normalize_reward(self, reward: float) -> float:
        """
        Normalize reward using running statistics.

        Args:
            reward: Raw reward value

        Returns:
            Normalized reward
        """
        if np.isnan(reward) or np.isinf(reward):
            return 0.0

        # Update running statistics
        self._reward_count += 1
        delta = reward - self._reward_mean
        self._reward_mean += delta / self._reward_count

        if self._reward_count > 1:
            delta2 = reward - self._reward_mean
            self._reward_std = np.sqrt(
                (self._reward_std**2 * (self._reward_count - 2) + delta * delta2)
                / (self._reward_count - 1)
            )

        # Normalize
        if self._reward_std > 1e-8:
            normalized_reward = (reward - self._reward_mean) / self._reward_std
            # Clip to prevent extreme values
            return np.clip(normalized_reward, -3.0, 3.0)
        else:
            return 0.0

    def compute(
        self,
        pnl: float,
        close_bonus: float,
        risk_penalty: float,
        cost_penalty: float,
        drawdown_penalty: float,
        volatility_penalty: float,
    ) -> float:
        """
        Compute shaped reward with proper validation and normalization.

        Args:
            pnl: Profit and loss
            close_bonus: Bonus for closing positions
            risk_penalty: Penalty for risk exposure
            cost_penalty: Penalty for transaction costs
            drawdown_penalty: Penalty for drawdown
            volatility_penalty: Penalty for volatility

        Returns:
            Shaped and normalized reward
        """
        # Validate inputs
        if not all(
            isinstance(x, (int, float))
            for x in [
                pnl,
                close_bonus,
                risk_penalty,
                cost_penalty,
                drawdown_penalty,
                volatility_penalty,
            ]
        ):
            if self.logger:
                self.logger.warning(
                    "Invalid reward components detected, using defaults"
                )
            pnl = close_bonus = risk_penalty = cost_penalty = drawdown_penalty = (
                volatility_penalty
            ) = 0.0

        # Check for NaN or inf values
        components = [
            pnl,
            close_bonus,
            risk_penalty,
            cost_penalty,
            drawdown_penalty,
            volatility_penalty,
        ]
        for i, comp in enumerate(components):
            if np.isnan(comp) or np.isinf(comp):
                if self.logger:
                    self.logger.warning(
                        f"Invalid reward component {i}: {comp}, setting to 0"
                    )
                components[i] = 0.0

        (
            pnl,
            close_bonus,
            risk_penalty,
            cost_penalty,
            drawdown_penalty,
            volatility_penalty,
        ) = components

        # Calculate weighted reward
        reward = (
            self.pnl_weight * pnl
            + self.close_rule_weight * close_bonus
            - self.risk_penalty_weight * risk_penalty
            - self.cost_weight * cost_penalty
            - self.drawdown_penalty_weight * drawdown_penalty
            - self.volatility_penalty_weight * volatility_penalty
        )

        # Normalize reward
        normalized_reward = self.normalize_reward(reward)

        # Apply reward scaling
        final_reward = normalized_reward * self.config.environment.reward_scale

        if self.logger:
            self.logger.debug(
                f"Reward components: pnl={pnl:.4f}, close_bonus={close_bonus:.4f}, "
                f"risk_penalty={risk_penalty:.4f}, cost_penalty={cost_penalty:.4f}, "
                f"drawdown_penalty={drawdown_penalty:.4f}, volatility_penalty={volatility_penalty:.4f}, "
                f"final_reward={final_reward:.4f}"
            )

        return float(final_reward)

    def get_reward_stats(self) -> Dict[str, float]:
        """Get reward statistics."""
        return {
            "reward_mean": self._reward_mean,
            "reward_std": self._reward_std,
            "reward_count": self._reward_count,
            "max_equity": self._max_equity,
            "current_drawdown": self.drawdown(),
            "current_volatility": self.realized_volatility(),
        }

    def reset(self):
        """Reset reward shaper state."""
        self._equity_history.clear()
        self._max_equity = 0.0
        self._initial_equity = 0.0
        self._position_count_history.clear()
        self._reward_mean = 0.0
        self._reward_std = 1.0
        self._reward_count = 0

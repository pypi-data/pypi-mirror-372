"""
Base environment for XTrade-AI Framework.

This module provides a base Gymnasium environment for trading simulation
with enhanced episode consistency and state generation capabilities.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import gymnasium as gym
import numpy as np
import pandas as pd
from gymnasium import spaces

logger = logging.getLogger(__name__)


@dataclass
class Position:
    """Enhanced position information."""

    symbol: str
    side: str  # 'long' or 'short'
    size: float
    entry_price: float
    current_price: float
    entry_time: datetime
    pnl: float = 0.0
    unrealized_pnl: float = 0.0
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    trailing_stop: Optional[float] = None
    max_profit: float = 0.0
    max_loss: float = 0.0

    @property
    def pnl_percentage(self) -> float:
        """Calculate PnL percentage."""
        if self.entry_price == 0:
            return 0.0
        if self.side == "long":
            return (self.current_price - self.entry_price) / self.entry_price
        else:
            return (self.entry_price - self.current_price) / self.entry_price

    @property
    def is_profitable(self) -> bool:
        """Check if position is profitable."""
        return self.unrealized_pnl > 0

    @property
    def duration(self) -> timedelta:
        """Calculate position duration."""
        return datetime.now() - self.entry_time


@dataclass
class Order:
    """Enhanced order information."""

    id: str
    symbol: str
    side: str  # 'buy', 'sell', 'close'
    size: float
    price: float
    order_type: str  # 'market', 'limit', 'stop', 'trailing_stop'
    status: str  # 'pending', 'filled', 'cancelled', 'rejected'
    timestamp: datetime
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    trailing_stop: Optional[float] = None


class BaseEnvironment(gym.Env):
    """
    Enhanced base trading environment with advanced features.

    This environment provides a foundation for trading simulation with:
    - Consistent episode lengths
    - Multiple open positions support
    - Dynamic state generation
    - Comprehensive reward calculation
    - Advanced risk management
    - Position sizing strategies
    - Market impact simulation
    - Realistic order execution
    """

    def __init__(
        self, config: Dict[str, Any], market_data: Optional[pd.DataFrame] = None
    ):
        """
        Initialize the base environment.

        Args:
            config: Configuration dictionary
            market_data: OHLCV market data
        """
        super().__init__()

        self.config = config
        self.market_data = market_data
        self.current_step = 0
        self.episode_step = 0
        self.max_episode_steps = config.get("max_episode_steps", 1000)

        # Trading state
        self.balance = config.get("initial_balance", 10000.0)
        self.initial_balance = self.balance
        self.equity = self.balance
        self.positions: List[Position] = []
        self.orders: List[Order] = []
        self.trades: List[Dict[str, Any]] = []
        self.closed_positions: List[Dict[str, Any]] = []

        # Trading parameters
        self.max_positions = config.get("max_positions", 10)
        self.commission_rate = config.get("commission_rate", 0.001)
        self.slippage = config.get("slippage", 0.0005)
        self.stop_loss = config.get("stop_loss", 0.02)
        self.take_profit = config.get("take_profit", 0.05)
        self.leverage = config.get("leverage", 1.0)
        self.margin_requirement = config.get("margin_requirement", 0.1)

        # Risk management
        self.max_drawdown = config.get("max_drawdown", 0.2)
        self.var_confidence = config.get("var_confidence", 0.95)
        self.max_correlation = config.get("max_correlation", 0.7)

        # Position sizing
        self.position_sizing = config.get("position_sizing", "fixed")
        self.risk_per_trade = config.get("risk_per_trade", 0.01)

        # Market impact simulation
        self.market_impact = config.get("market_impact", False)
        self.impact_factor = config.get("impact_factor", 0.0001)

        # State and action spaces
        self.state_dim = config.get("state_dim", 545)
        self.action_dim = config.get("action_dim", 4)

        # Define action and observation spaces
        self.action_space = spaces.Discrete(self.action_dim)
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(self.state_dim,), dtype=np.float32
        )

        # Episode tracking
        self.episode_rewards = []
        self.episode_pnl = 0.0
        self.episode_trades = 0
        self.max_equity = self.balance
        self.max_drawdown_episode = 0.0

        # Performance metrics
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_pnl = 0.0
        self.max_drawdown_total = 0.0

        logger.info(
            f"BaseEnvironment initialized with {self.state_dim} state dimensions"
        )

    def reset(self, seed: Optional[int] = None) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Reset the environment for a new episode.

        Args:
            seed: Random seed for reproducibility

        Returns:
            Tuple of (initial_state, info)
        """
        super().reset(seed=seed)

        # Reset episode state
        self.current_step = 0
        self.episode_step = 0
        self.episode_rewards = []
        self.episode_pnl = 0.0
        self.episode_trades = 0
        self.max_equity = self.balance
        self.max_drawdown_episode = 0.0

        # Reset trading state
        self.balance = self.initial_balance
        self.equity = self.balance
        self.positions = []
        self.orders = []
        self.trades = []

        # Get initial state
        initial_state = self._get_state()

        info = {
            "balance": self.balance,
            "equity": self.equity,
            "positions": len(self.positions),
            "episode_step": self.episode_step,
            "max_episode_steps": self.max_episode_steps,
        }

        logger.debug(f"Environment reset. Initial state shape: {initial_state.shape}")
        return initial_state, info

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """
        Take a step in the environment.

        Args:
            action: Action to take (0: hold, 1: buy, 2: sell, 3: close)

        Returns:
            Tuple of (state, reward, terminated, truncated, info)
        """
        # Execute action
        self._execute_action(action)

        # Update positions and calculate P&L
        self._update_positions()

        # Update equity
        self._update_equity()

        # Calculate reward
        reward = self._calculate_reward()

        # Update episode state
        self.episode_step += 1
        self.current_step += 1
        self.episode_rewards.append(reward)

        # Check termination conditions
        terminated = self._check_termination()
        truncated = self.episode_step >= self.max_episode_steps

        # Get new state
        state = self._get_state()

        # Prepare info
        info = self._get_info()

        return state, reward, terminated, truncated, info

    def _execute_action(self, action: int) -> None:
        """
        Execute the given action with enhanced logic.

        Args:
            action: Action to execute
        """
        if self.market_data is None or self.current_step >= len(self.market_data):
            return

        current_price = self.market_data.iloc[self.current_step]["close"]

        if action == 0:  # Hold
            pass
        elif action == 1:  # Buy/Long
            self._open_position("long", current_price)
        elif action == 2:  # Sell/Short
            self._open_position("short", current_price)
        elif action == 3:  # Close
            self._close_positions(current_price)

    def _open_position(self, side: str, price: float) -> None:
        """
        Open a new position with advanced position sizing.

        Args:
            side: Position side ('long' or 'short')
            price: Entry price
        """
        if len(self.positions) >= self.max_positions:
            return

        # Check risk limits
        if not self._check_risk_limits(side, price):
            return

        # Calculate position size based on strategy
        position_size = self._calculate_position_size(side, price)

        if position_size <= 0:
            return

        # Apply market impact if enabled
        if self.market_impact:
            price = self._apply_market_impact(price, position_size, side)

        # Apply slippage
        if side == "long":
            entry_price = price * (1 + self.slippage)
        else:
            entry_price = price * (1 - self.slippage)

        # Calculate margin requirement
        margin_required = position_size * self.margin_requirement / self.leverage

        if margin_required > self.balance:
            logger.warning(
                f"Insufficient margin for position: {margin_required} > {self.balance}"
            )
            return

        # Create position
        position = Position(
            symbol="default",
            side=side,
            size=position_size,
            entry_price=entry_price,
            current_price=price,
            entry_time=datetime.now(),
            stop_loss=(
                entry_price * (1 - self.stop_loss)
                if side == "long"
                else entry_price * (1 + self.stop_loss)
            ),
            take_profit=(
                entry_price * (1 + self.take_profit)
                if side == "long"
                else entry_price * (1 - self.take_profit)
            ),
        )

        self.positions.append(position)

        # Deduct commission and margin
        commission = position_size * self.commission_rate
        self.balance -= commission + margin_required

        logger.debug(
            f"Opened {side} position at {entry_price:.4f}, size: {position_size:.2f}"
        )

    def _calculate_position_size(self, side: str, price: float) -> float:
        """
        Calculate position size based on strategy.

        Args:
            side: Position side
            price: Entry price

        Returns:
            Position size
        """
        if self.position_sizing == "fixed":
            return self.balance * 0.1  # 10% of balance

        elif self.position_sizing == "kelly":
            # Kelly criterion for position sizing
            win_rate = self.winning_trades / max(self.total_trades, 1)
            avg_win = self.total_pnl / max(self.winning_trades, 1)
            avg_loss = abs(self.total_pnl) / max(self.losing_trades, 1)

            if avg_loss > 0:
                kelly_fraction = (
                    win_rate * avg_win - (1 - win_rate) * avg_loss
                ) / avg_win
                kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Cap at 25%
                return self.balance * kelly_fraction
            else:
                return self.balance * 0.1

        elif self.position_sizing == "risk_based":
            # Risk-based position sizing
            risk_amount = self.balance * self.risk_per_trade
            stop_distance = price * self.stop_loss
            if stop_distance > 0:
                return risk_amount / stop_distance
            else:
                return self.balance * 0.1

        else:
            return self.balance * 0.1

    def _check_risk_limits(self, side: str, price: float) -> bool:
        """
        Check if opening position violates risk limits.

        Args:
            side: Position side
            price: Entry price

        Returns:
            True if position can be opened
        """
        # Check drawdown limit
        current_drawdown = (self.max_equity - self.equity) / self.max_equity
        if current_drawdown > self.max_drawdown:
            return False

        # Check correlation limit
        if len(self.positions) > 0:
            # Simple correlation check based on position sides
            same_side_positions = sum(1 for pos in self.positions if pos.side == side)
            if same_side_positions / len(self.positions) > self.max_correlation:
                return False

        return True

    def _apply_market_impact(self, price: float, size: float, side: str) -> float:
        """
        Apply market impact to price.

        Args:
            price: Original price
            size: Position size
            side: Position side

        Returns:
            Adjusted price
        """
        impact = size * self.impact_factor
        if side == "long":
            return price * (1 + impact)
        else:
            return price * (1 - impact)

    def _close_positions(self, price: float) -> None:
        """
        Close all open positions with enhanced logic.

        Args:
            price: Current market price
        """
        for position in self.positions[
            :
        ]:  # Copy list to avoid modification during iteration
            # Apply slippage
            if position.side == "long":
                exit_price = price * (1 - self.slippage)
            else:
                exit_price = price * (1 + self.slippage)

            # Calculate P&L
            if position.side == "long":
                pnl = (exit_price - position.entry_price) * position.size
            else:
                pnl = (position.entry_price - exit_price) * position.size

            # Deduct commission
            commission = position.size * self.commission_rate
            pnl -= commission

            # Update balance and equity
            margin_returned = position.size * self.margin_requirement / self.leverage
            self.balance += position.size + pnl + margin_returned
            self.equity += pnl
            self.episode_pnl += pnl
            self.episode_trades += 1
            self.total_trades += 1

            # Update trade statistics
            if pnl > 0:
                self.winning_trades += 1
            else:
                self.losing_trades += 1

            self.total_pnl += pnl

            # Record trade
            trade = {
                "side": position.side,
                "entry_price": position.entry_price,
                "exit_price": exit_price,
                "size": position.size,
                "pnl": pnl,
                "commission": commission,
                "duration": position.duration,
                "entry_time": position.entry_time,
                "exit_time": datetime.now(),
            }
            self.trades.append(trade)
            self.closed_positions.append(trade)

            # Remove position
            self.positions.remove(position)

            logger.debug(f"Closed {position.side} position. P&L: {pnl:.2f}")

    def _update_positions(self) -> None:
        """Update current prices and unrealized P&L for all positions."""
        if self.market_data is None or self.current_step >= len(self.market_data):
            return

        current_price = self.market_data.iloc[self.current_step]["close"]

        for position in self.positions:
            position.current_price = current_price

            # Calculate unrealized P&L
            if position.side == "long":
                position.unrealized_pnl = (
                    current_price - position.entry_price
                ) * position.size
            else:
                position.unrealized_pnl = (
                    position.entry_price - current_price
                ) * position.size

            # Update max profit/loss
            if position.unrealized_pnl > position.max_profit:
                position.max_profit = position.unrealized_pnl
            if position.unrealized_pnl < position.max_loss:
                position.max_loss = position.unrealized_pnl

            # Check stop loss and take profit
            if self._should_close_position(position):
                self._close_positions(current_price)
                break

    def _should_close_position(self, position: Position) -> bool:
        """
        Check if position should be closed due to stop loss or take profit.

        Args:
            position: Position to check

        Returns:
            True if position should be closed
        """
        if position.side == "long":
            loss_ratio = (
                position.entry_price - position.current_price
            ) / position.entry_price
            profit_ratio = (
                position.current_price - position.entry_price
            ) / position.entry_price
        else:
            loss_ratio = (
                position.current_price - position.entry_price
            ) / position.entry_price
            profit_ratio = (
                position.entry_price - position.current_price
            ) / position.entry_price

        # Check stop loss
        if loss_ratio >= self.stop_loss:
            return True

        # Check take profit
        if profit_ratio >= self.take_profit:
            return True

        # Check trailing stop
        if position.trailing_stop is not None:
            if position.side == "long":
                trailing_stop_price = (
                    position.max_profit / position.size
                    + position.entry_price
                    - position.trailing_stop
                )
                if position.current_price <= trailing_stop_price:
                    return True
            else:
                trailing_stop_price = (
                    position.entry_price
                    - position.max_profit / position.size
                    + position.trailing_stop
                )
                if position.current_price >= trailing_stop_price:
                    return True

        return False

    def _update_equity(self) -> None:
        """Update equity and track maximum equity."""
        unrealized_pnl = sum(pos.unrealized_pnl for pos in self.positions)
        self.equity = self.balance + unrealized_pnl

        if self.equity > self.max_equity:
            self.max_equity = self.equity

        # Update drawdown
        current_drawdown = (self.max_equity - self.equity) / self.max_equity
        if current_drawdown > self.max_drawdown_episode:
            self.max_drawdown_episode = current_drawdown

        if current_drawdown > self.max_drawdown_total:
            self.max_drawdown_total = current_drawdown

    def _calculate_reward(self) -> float:
        """
        Calculate reward for the current step with enhanced logic.

        Returns:
            Reward value
        """
        # Calculate total P&L
        total_pnl = self.episode_pnl

        # Add unrealized P&L
        for position in self.positions:
            total_pnl += position.unrealized_pnl

        # Calculate return
        total_return = total_pnl / self.initial_balance

        # Base reward based on return
        reward = total_return

        # Penalty for too many positions
        if len(self.positions) > self.max_positions * 0.8:
            reward -= 0.001

        # Penalty for low balance
        if self.balance < self.initial_balance * 0.5:
            reward -= 0.01

        # Penalty for high drawdown
        current_drawdown = (self.max_equity - self.equity) / self.max_equity
        if current_drawdown > self.max_drawdown * 0.8:
            reward -= 0.005

        # Bonus for good risk management
        if (
            len(self.positions) <= self.max_positions * 0.5
            and current_drawdown < self.max_drawdown * 0.3
        ):
            reward += 0.001

        return reward

    def _check_termination(self) -> bool:
        """
        Check if episode should terminate.

        Returns:
            True if episode should terminate
        """
        # Terminate if balance is too low
        if self.balance < self.initial_balance * 0.1:
            return True

        # Terminate if drawdown is too high
        current_drawdown = (self.max_equity - self.equity) / self.max_equity
        if current_drawdown > self.max_drawdown:
            return True

        # Terminate if no more data
        if (
            self.market_data is not None
            and self.current_step >= len(self.market_data) - 1
        ):
            return True

        return False

    def _get_state(self) -> np.ndarray:
        """
        Generate current state vector with enhanced features.

        Returns:
            State vector as numpy array
        """
        if self.market_data is None or self.current_step >= len(self.market_data):
            return np.zeros(self.state_dim, dtype=np.float32)

        # Get current market data
        current_data = self.market_data.iloc[self.current_step]

        # Basic OHLCV features
        state = [
            current_data["open"],
            current_data["high"],
            current_data["low"],
            current_data["close"],
            current_data["volume"],
        ]

        # Add technical indicators if available
        technical_columns = [
            col
            for col in self.market_data.columns
            if col not in ["open", "high", "low", "close", "volume"]
        ]

        for col in technical_columns:
            if col in current_data:
                state.append(current_data[col])
            else:
                state.append(0.0)

        # Add position information
        state.extend(self._get_position_features())

        # Add account information
        state.extend(self._get_account_features())

        # Add risk metrics
        state.extend(self._get_risk_features())

        # Add market features
        state.extend(self._get_market_features())

        # Pad or truncate to match state_dim
        if len(state) < self.state_dim:
            state.extend([0.0] * (self.state_dim - len(state)))
        elif len(state) > self.state_dim:
            state = state[: self.state_dim]

        return np.array(state, dtype=np.float32)

    def _get_position_features(self) -> List[float]:
        """
        Get position-related features.

        Returns:
            List of position features
        """
        features = []

        # Number of positions
        features.append(len(self.positions))

        # Total position value
        total_value = sum(pos.size for pos in self.positions)
        features.append(total_value)

        # Average unrealized P&L
        if self.positions:
            avg_pnl = sum(pos.unrealized_pnl for pos in self.positions) / len(
                self.positions
            )
            features.append(avg_pnl)
        else:
            features.append(0.0)

        # Long vs short ratio
        long_positions = sum(1 for pos in self.positions if pos.side == "long")
        short_positions = len(self.positions) - long_positions
        features.extend([long_positions, short_positions])

        # Position duration features
        if self.positions:
            avg_duration = sum(
                pos.duration.total_seconds() for pos in self.positions
            ) / len(self.positions)
            features.append(avg_duration)
        else:
            features.append(0.0)

        return features

    def _get_account_features(self) -> List[float]:
        """
        Get account-related features.

        Returns:
            List of account features
        """
        features = []

        # Balance and equity
        features.extend([self.balance, self.equity])

        # Return
        total_return = (self.equity - self.initial_balance) / self.initial_balance
        features.append(total_return)

        # Number of trades
        features.append(self.episode_trades)

        # Average reward
        if self.episode_rewards:
            avg_reward = sum(self.episode_rewards) / len(self.episode_rewards)
            features.append(avg_reward)
        else:
            features.append(0.0)

        # Win rate
        if self.total_trades > 0:
            win_rate = self.winning_trades / self.total_trades
            features.append(win_rate)
        else:
            features.append(0.0)

        return features

    def _get_risk_features(self) -> List[float]:
        """
        Get risk-related features.

        Returns:
            List of risk features
        """
        features = []

        # Current drawdown
        current_drawdown = (self.max_equity - self.equity) / self.max_equity
        features.append(current_drawdown)

        # Maximum drawdown
        features.append(self.max_drawdown_episode)

        # Risk per trade
        features.append(self.risk_per_trade)

        # Position concentration
        if self.positions:
            total_value = sum(pos.size for pos in self.positions)
            if total_value > 0:
                concentration = max(pos.size for pos in self.positions) / total_value
                features.append(concentration)
            else:
                features.append(0.0)
        else:
            features.append(0.0)

        return features

    def _get_market_features(self) -> List[float]:
        """
        Get market-related features.

        Returns:
            List of market features
        """
        features = []

        if self.market_data is not None and self.current_step > 0:
            # Price change
            current_price = self.market_data.iloc[self.current_step]["close"]
            prev_price = self.market_data.iloc[self.current_step - 1]["close"]
            price_change = (current_price - prev_price) / prev_price
            features.append(price_change)

            # Volume change
            current_volume = self.market_data.iloc[self.current_step]["volume"]
            prev_volume = self.market_data.iloc[self.current_step - 1]["volume"]
            if prev_volume > 0:
                volume_change = (current_volume - prev_volume) / prev_volume
                features.append(volume_change)
            else:
                features.append(0.0)

            # Volatility (rolling standard deviation of returns)
            if self.current_step >= 20:
                returns = self.market_data.iloc[
                    self.current_step - 20 : self.current_step
                ]["close"].pct_change()
                volatility = returns.std()
                features.append(volatility)
            else:
                features.append(0.0)
        else:
            features.extend([0.0, 0.0, 0.0])

        return features

    def _get_info(self) -> Dict[str, Any]:
        """
        Get current environment information.

        Returns:
            Dictionary with environment information
        """
        return {
            "balance": self.balance,
            "equity": self.equity,
            "positions": len(self.positions),
            "episode_step": self.episode_step,
            "max_episode_steps": self.max_episode_steps,
            "episode_pnl": self.episode_pnl,
            "episode_trades": self.episode_trades,
            "total_return": (self.equity - self.initial_balance) / self.initial_balance,
            "avg_reward": (
                np.mean(self.episode_rewards) if self.episode_rewards else 0.0
            ),
            "close_decision": len(self.positions) > 0,
            "current_drawdown": (self.max_equity - self.equity) / self.max_equity,
            "max_drawdown": self.max_drawdown_episode,
            "win_rate": self.winning_trades / max(self.total_trades, 1),
        }

    def render(self):
        """Render the environment (not implemented)."""
        pass

    def close(self):
        """Close the environment."""
        pass

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get episode statistics.

        Returns:
            Dictionary with episode statistics
        """
        total_return = (self.equity - self.initial_balance) / self.initial_balance

        return {
            "initial_balance": self.initial_balance,
            "final_balance": self.balance,
            "final_equity": self.equity,
            "total_return": total_return,
            "total_trades": self.episode_trades,
            "episode_length": self.episode_step,
            "avg_reward": (
                np.mean(self.episode_rewards) if self.episode_rewards else 0.0
            ),
            "max_reward": max(self.episode_rewards) if self.episode_rewards else 0.0,
            "min_reward": min(self.episode_rewards) if self.episode_rewards else 0.0,
            "max_drawdown": self.max_drawdown_episode,
            "win_rate": self.winning_trades / max(self.total_trades, 1),
            "trades": self.trades,
        }

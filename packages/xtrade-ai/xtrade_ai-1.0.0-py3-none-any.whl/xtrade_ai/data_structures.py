"""
XTrade-AI Data Structures

Defines dataclasses for storing and passing data between modules.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


class ActionType(Enum):
    """Trading action types"""

    BUY = 0
    SELL = 1
    HOLD = 2
    CLOSE = 3


class MarketRegime(Enum):
    """Market regime types for meta-learning"""

    BULLISH = 0
    BEARISH = 1
    NEUTRAL = 2
    VOLATILE = 3


@dataclass
class MarketState:
    """Current market state information"""

    timestamp: float
    price: float
    volume: float
    bid: float
    ask: float
    spread: float
    volatility: float
    trend: float
    momentum: float

    def to_array(self) -> np.ndarray:
        """Convert to numpy array"""
        return np.array(
            [
                self.price,
                self.volume,
                self.bid,
                self.ask,
                self.spread,
                self.volatility,
                self.trend,
                self.momentum,
            ]
        )


@dataclass
class Position:
    """Trading position information"""

    position_id: str
    symbol: str
    side: str  # 'long' or 'short'
    entry_price: float
    current_price: float
    quantity: float
    entry_time: float
    unrealized_pnl: float
    realized_pnl: float = 0.0
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

    @property
    def pnl_percentage(self) -> float:
        """Calculate PnL percentage"""
        if self.entry_price == 0:
            return 0.0
        if self.side == "long":
            return (self.current_price - self.entry_price) / self.entry_price
        else:
            return (self.entry_price - self.current_price) / self.entry_price

    @property
    def is_profitable(self) -> bool:
        """Check if position is profitable"""
        return self.unrealized_pnl > 0


@dataclass
class TradingDecision:
    """Trading decision from action selector"""

    action: ActionType
    confidence: float
    position_size: float = 0.0
    reasons: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_discrete_action(self) -> int:
        """Convert to discrete action for environment"""
        return self.action.value


@dataclass
class CloseOrderDecision:
    """Close order decision from close order module"""

    should_close: bool
    close_indices: List[int] = field(default_factory=list)
    close_probabilities: List[float] = field(default_factory=list)
    close_all: bool = False
    reasons: List[str] = field(default_factory=list)

    def get_positions_to_close(self, positions: List[Position]) -> List[Position]:
        """Get positions that should be closed"""
        if self.close_all:
            return positions
        return [positions[i] for i in self.close_indices if i < len(positions)]


@dataclass
class RiskAssessment:
    """Risk assessment from risk management module"""

    risk_score: float  # 0-1, higher is riskier
    position_size_adjustment: float  # Multiplier for position size
    max_positions_allowed: int
    stop_loss_adjustment: float
    take_profit_adjustment: float
    warnings: List[str] = field(default_factory=list)

    def is_high_risk(self, threshold: float = 0.7) -> bool:
        """Check if risk is above threshold"""
        return self.risk_score > threshold


@dataclass
class TechnicalSignals:
    """Technical analysis signals"""

    trend_signal: float  # -1 to 1 (bearish to bullish)
    momentum_signal: float  # -1 to 1
    volatility_signal: float  # 0 to 1 (low to high)
    volume_signal: float  # -1 to 1
    support_resistance: Dict[str, float] = field(default_factory=dict)
    patterns: List[str] = field(default_factory=list)

    def get_overall_signal(self) -> float:
        """Get overall signal strength"""
        weights = [0.3, 0.3, 0.2, 0.2]  # Trend, momentum, volatility, volume
        signals = [
            self.trend_signal,
            self.momentum_signal,
            -abs(self.volatility_signal - 0.5),
            self.volume_signal,
        ]
        return sum(w * s for w, s in zip(weights, signals))


@dataclass
class ExperienceRecord:
    """Experience record for replay buffer"""

    state: np.ndarray
    action: int
    reward: float
    next_state: np.ndarray
    done: bool
    info: Dict[str, Any] = field(default_factory=dict)

    def to_tuple(self) -> Tuple:
        """Convert to tuple for compatibility"""
        return (self.state, self.action, self.reward, self.next_state, self.done)


@dataclass
class ModelPrediction:
    """Prediction from a deep learning model"""

    model_name: str
    prediction: Any  # Can be action, signal, etc.
    confidence: float
    features_used: Optional[List[str]] = None
    computation_time: float = 0.0

    def is_confident(self, threshold: float = 0.6) -> bool:
        """Check if prediction confidence is above threshold"""
        return self.confidence >= threshold


@dataclass
class TrainingMetrics:
    """Training metrics for monitoring"""

    epoch: int
    loss: float
    accuracy: float = 0.0
    val_loss: float = 0.0
    val_accuracy: float = 0.0
    learning_rate: float = 0.0
    additional_metrics: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
        return {
            "epoch": self.epoch,
            "loss": self.loss,
            "accuracy": self.accuracy,
            "val_loss": self.val_loss,
            "val_accuracy": self.val_accuracy,
            "learning_rate": self.learning_rate,
            **self.additional_metrics,
        }


@dataclass
class TradingMetrics:
    """Trading performance metrics"""

    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_pnl: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    win_rate: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    profit_factor: float = 0.0

    def update(self, trade_pnl: float):
        """Update metrics with new trade"""
        self.total_trades += 1
        self.total_pnl += trade_pnl

        if trade_pnl > 0:
            self.winning_trades += 1
            self.avg_win = (
                (self.avg_win * (self.winning_trades - 1)) + trade_pnl
            ) / self.winning_trades
        else:
            self.losing_trades += 1
            self.avg_loss = (
                (self.avg_loss * (self.losing_trades - 1)) + abs(trade_pnl)
            ) / self.losing_trades

        self.win_rate = (
            self.winning_trades / self.total_trades if self.total_trades > 0 else 0
        )

        if self.avg_loss > 0:
            self.profit_factor = self.avg_win / self.avg_loss

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
        return {
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "total_pnl": self.total_pnl,
            "max_drawdown": self.max_drawdown,
            "sharpe_ratio": self.sharpe_ratio,
            "win_rate": self.win_rate,
            "avg_win": self.avg_win,
            "avg_loss": self.avg_loss,
            "profit_factor": self.profit_factor,
        }


@dataclass
class StateRepresentation:
    """Complete state representation for models"""

    ohlcv_data: np.ndarray  # Shape: (window_size, 5)
    technical_indicators: np.ndarray  # Shape: (n_indicators,)
    position_info: np.ndarray  # Shape: (max_positions, position_features)
    market_state: MarketState
    account_info: Dict[str, float]

    def flatten(self) -> np.ndarray:
        """Flatten to 1D array for model input"""
        flattened = []

        # Flatten OHLCV
        flattened.extend(self.ohlcv_data.flatten())

        # Add technical indicators
        flattened.extend(self.technical_indicators)

        # Flatten position info
        flattened.extend(self.position_info.flatten())

        # Add market state
        flattened.extend(self.market_state.to_array())

        # Add account info
        flattened.extend(
            [
                self.account_info.get("balance", 0),
                self.account_info.get("equity", 0),
                self.account_info.get("margin_used", 0),
                self.account_info.get("free_margin", 0),
            ]
        )

        return np.array(flattened, dtype=np.float32)

    def to_sequence(self, sequence_length: int) -> np.ndarray:
        """Convert to sequence for LSTM/GRU models"""
        # This is a simplified version - in practice, you'd maintain a history
        flat = self.flatten()
        return np.tile(flat, (sequence_length, 1))


@dataclass
class ModelCheckpoint:
    """Model checkpoint information"""

    model_name: str
    epoch: int
    timestamp: float
    metrics: Dict[str, float]
    file_path: str
    config: Dict[str, Any] = field(default_factory=dict)

    def is_better_than(
        self, other: "ModelCheckpoint", metric: str = "val_loss"
    ) -> bool:
        """Compare checkpoints based on metric"""
        if metric not in self.metrics or metric not in other.metrics:
            return False

        # For loss metrics, lower is better
        if "loss" in metric:
            return self.metrics[metric] < other.metrics[metric]
        # For accuracy/reward metrics, higher is better
        else:
            return self.metrics[metric] > other.metrics[metric]


@dataclass
class Order:
    """Order information."""

    id: str
    symbol: str
    side: str  # 'buy', 'sell', 'close'
    size: float
    price: float
    status: str  # 'pending', 'filled', 'cancelled'
    timestamp: int


@dataclass
class Trade:
    """Trade information."""

    id: str
    symbol: str
    side: str
    size: float
    entry_price: float
    exit_price: float
    pnl: float
    commission: float
    timestamp: int


@dataclass
class Portfolio:
    """Portfolio information."""

    balance: float
    positions: List[Position]
    orders: List[Order]
    trades: List[Trade]
    total_pnl: float = 0.0
    unrealized_pnl: float = 0.0


@dataclass
class CloseOrderDecision:
    """Close order decision structure."""

    should_close: bool
    close_reason: str
    confidence: float
    urgency: str  # 'low', 'medium', 'high'
    metadata: Optional[Dict[str, Any]] = None

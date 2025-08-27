from typing import List

import torch
import torch.nn as nn
import torch.nn.functional as F

try:
    from ..config import XTradeAIConfig
    from ..data_structures import Position, RiskAssessment
except ImportError:
    from config import XTradeAIConfig
    from data_structures import Position, RiskAssessment


class RiskManagementModule(nn.Module):
    """GRU-based module to assess risk and adjust position sizing."""

    def __init__(self, config: XTradeAIConfig, feature_dim: int = 8):
        super().__init__()
        self.config = config
        hidden_dim = config.model.hidden_dim
        num_layers = config.model.num_layers
        self.gru = nn.GRU(
            input_size=feature_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
        )
        self.head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 2),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        output, _ = self.gru(x)
        h = output[:, -1, :]
        out = self.head(h)
        return out

    @torch.no_grad()
    def assess(
        self, market_features: List[float], positions: List[Position]
    ) -> RiskAssessment:
        # market_features: a list of scalar features like volatility, spread, etc.
        x = torch.tensor([[market_features]], dtype=torch.float32)
        out = self.forward(x)[0]
        risk_raw = float(torch.sigmoid(out[0]).item())
        adj_raw = float(torch.sigmoid(out[1]).item())
        max_positions_allowed = max(
            1, int(self.config.trading.max_positions * (1.0 - 0.5 * risk_raw))
        )
        stop_loss_adjustment = max(
            1e-6, self.config.trading.stop_loss * (1.0 + 0.5 * risk_raw)
        )
        take_profit_adjustment = max(
            1e-6, self.config.trading.take_profit * (1.0 - 0.25 * risk_raw)
        )
        warnings = []
        if risk_raw > 0.7:
            warnings.append("high_risk_market")
        return RiskAssessment(
            risk_score=risk_raw,
            position_size_adjustment=max(0.1, min(1.5, adj_raw * 2.0)),
            max_positions_allowed=max_positions_allowed,
            stop_loss_adjustment=stop_loss_adjustment,
            take_profit_adjustment=take_profit_adjustment,
            warnings=warnings,
        )

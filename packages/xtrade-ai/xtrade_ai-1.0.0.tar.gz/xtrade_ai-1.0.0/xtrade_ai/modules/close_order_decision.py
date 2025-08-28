from typing import List

import torch
import torch.nn as nn
import torch.nn.functional as F

try:
    from ..attention_mechanism import TransformerBlock
    from ..config import XTradeAIConfig
    from ..data_structures import CloseOrderDecision, Position
except ImportError:
    from attention_mechanism import TransformerBlock
    from config import XTradeAIConfig
    from data_structures import CloseOrderDecision, Position


class CloseOrderDecisionMaker(nn.Module):
    """Transformer-based module to decide which positions to close."""

    def __init__(self, config: XTradeAIConfig, position_feature_dim: int = 8):
        super().__init__()
        self.config = config
        d_model = config.model.hidden_dim
        self.input_proj = nn.Linear(position_feature_dim, d_model)
        self.transformer = TransformerBlock(
            d_model=d_model,
            num_heads=config.model.num_heads,
            d_ff=config.model.ff_dim,
            dropout=config.model.dropout_rate,
        )
        self.head = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.ReLU(),
            nn.Dropout(config.model.dropout_rate),
            nn.Linear(d_model // 2, 1),
            nn.Sigmoid(),
        )

    def forward(self, position_features: torch.Tensor) -> torch.Tensor:
        # position_features: (batch, num_positions, feat)
        h = self.input_proj(position_features)
        h = self.transformer(h)
        proba = self.head(h).squeeze(-1)
        return proba

    @torch.no_grad()
    def make_decision(self, positions: List[Position]) -> CloseOrderDecision:
        if not positions:
            return CloseOrderDecision(should_close=False)
        features = []
        for p in positions:
            features.append(
                [
                    1.0 if p.side == "long" else -1.0,
                    float(p.entry_price),
                    float(p.current_price),
                    float(p.quantity),
                    float(p.unrealized_pnl),
                    float(p.pnl_percentage),
                    float(p.take_profit or 0.0),
                    float(p.stop_loss or 0.0),
                ]
            )
        position_tensor = torch.tensor([features], dtype=torch.float32)
        proba = self.forward(position_tensor)[0]  # (num_positions,)
        proba_list = proba.tolist()
        profit_threshold = self.config.trading.profit_threshold
        close_indices = [
            i for i, p in enumerate(positions) if p.pnl_percentage >= profit_threshold
        ]
        selected = []
        for i in close_indices:
            if proba_list[i] >= 0.5:
                selected.append(i)
        should_close = len(selected) > 0
        return CloseOrderDecision(
            should_close=should_close,
            close_indices=selected,
            close_probabilities=[proba_list[i] for i in selected],
            close_all=False,
            reasons=["probabilistic_close", f"selected={len(selected)}"],
        )

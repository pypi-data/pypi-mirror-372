from typing import Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

from ..config import XTradeAIConfig
from ..data_structures import MarketRegime


class MetaLearningModule(nn.Module):
    """LSTM-based market regime detector (MAML-inspired skeleton)."""

    def __init__(self, config: XTradeAIConfig):
        super().__init__()
        self.config = config
        input_dim = config.model.state_dim
        hidden_dim = config.model.hidden_dim
        num_layers = config.model.num_layers
        self.lstm = nn.LSTM(
            input_dim, hidden_dim, num_layers=num_layers, batch_first=True
        )
        self.dropout = nn.Dropout(config.model.dropout_rate)
        self.head = nn.Linear(hidden_dim, 3)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch, seq_len, state_dim)
        output, _ = self.lstm(x)
        h = output[:, -1, :]
        h = self.dropout(h)
        logits = self.head(h)
        return logits

    @torch.no_grad()
    def predict_regime(self, x: torch.Tensor) -> Tuple[MarketRegime, float]:
        logits = self.forward(x)
        probs = F.softmax(logits, dim=-1)
        conf, idx = probs.max(dim=-1)
        label = idx.item()
        if label == 0:
            regime = MarketRegime.BULLISH
        elif label == 1:
            regime = MarketRegime.BEARISH
        else:
            regime = MarketRegime.NEUTRAL
        return regime, float(conf.item())

    def inner_loop_update(self, loss: torch.Tensor, lr: float) -> None:
        loss.backward()
        for p in self.parameters():
            if p.grad is not None:
                p.data -= lr * p.grad
                p.grad.zero_()

    def train_step(
        self,
        batch_x: torch.Tensor,
        batch_y: torch.Tensor,
        optimizer: torch.optim.Optimizer,
    ) -> float:
        self.train()
        optimizer.zero_grad()
        logits = self.forward(batch_x)
        loss = F.cross_entropy(logits, batch_y)
        loss.backward()
        optimizer.step()
        return float(loss.item())

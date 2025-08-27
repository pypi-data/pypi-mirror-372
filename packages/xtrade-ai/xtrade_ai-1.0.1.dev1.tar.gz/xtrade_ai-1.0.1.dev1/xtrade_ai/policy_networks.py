from typing import Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

try:
    from .attention_mechanism import TransformerBlock
    from .config import XTradeAIConfig
except ImportError:
    from attention_mechanism import TransformerBlock
    from config import XTradeAIConfig


class AttentionPolicyNetwork(nn.Module):
    """Self-attention based policy and value network for RL algorithms."""

    def __init__(self, state_dim: int, action_dim: int, config: XTradeAIConfig):
        super().__init__()
        self.config = config
        d_model = config.model.hidden_dim
        self.input_proj = nn.Linear(state_dim, d_model)
        self.transformer = TransformerBlock(
            d_model=d_model,
            num_heads=config.model.num_heads,
            d_ff=config.model.ff_dim,
            dropout=config.model.dropout_rate,
        )
        self.policy_head = nn.Sequential(
            nn.Linear(d_model, d_model),
            nn.ReLU(),
            nn.Dropout(config.model.dropout_rate),
            nn.Linear(d_model, action_dim),
        )
        self.value_head = nn.Sequential(
            nn.Linear(d_model, d_model),
            nn.ReLU(),
            nn.Dropout(config.model.dropout_rate),
            nn.Linear(d_model, 1),
        )

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        # x: (batch, state_dim)
        h = self.input_proj(x)  # (batch, d_model)
        # add a fake sequence length of 1 for transformer block
        h = h.unsqueeze(1)
        h = self.transformer(h)
        h = h.squeeze(1)
        logits = self.policy_head(h)
        value = self.value_head(h)
        return logits, value

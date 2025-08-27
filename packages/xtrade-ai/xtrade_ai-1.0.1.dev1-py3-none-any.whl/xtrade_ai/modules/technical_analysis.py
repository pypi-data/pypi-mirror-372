import torch
import torch.nn as nn
import torch.nn.functional as F

try:
    from ..config import XTradeAIConfig
except ImportError:
    from config import XTradeAIConfig


class TechnicalAnalysisModule(nn.Module):
    """CNN-LSTM for pattern-based buy/sell/hold signal classification."""

    def __init__(
        self,
        config: XTradeAIConfig,
        input_channels: int = 1,
        seq_len: int = 60,
        feature_dim: int = 32,
    ):
        super().__init__()
        self.config = config
        self.conv = nn.Conv1d(
            input_channels,
            config.model.num_filters,
            kernel_size=config.model.kernel_size,
            padding="same",
        )
        self.lstm = nn.LSTM(
            input_size=config.model.num_filters,
            hidden_size=config.model.hidden_dim,
            num_layers=config.model.num_layers,
            batch_first=True,
        )
        self.dropout = nn.Dropout(config.model.dropout_rate)
        self.head = nn.Linear(config.model.hidden_dim, 3)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch, seq_len, feature_dim) -> treat features as channels
        x = x.transpose(1, 2)  # (batch, feature_dim, seq_len)
        h = self.conv(x)  # (batch, filters, seq_len)
        h = F.relu(h)
        h = h.transpose(1, 2)  # (batch, seq_len, filters)
        out, _ = self.lstm(h)
        h_last = out[:, -1, :]
        h_last = self.dropout(h_last)
        logits = self.head(h_last)
        return logits

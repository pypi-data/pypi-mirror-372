import torch
import torch.nn as nn

try:
    from ..config import XTradeAIConfig
except ImportError:
    from config import XTradeAIConfig


class AdaptiveIndicatorModule(nn.Module):
    """Autoencoder to generate compact adaptive indicators."""

    def __init__(self, config: XTradeAIConfig, input_dim: int = 32):
        super().__init__()
        self.config = config
        ed = config.model.encoding_dim
        h = config.model.hidden_dim
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, h), nn.ReLU(), nn.Linear(h, ed)
        )
        self.decoder = nn.Sequential(
            nn.Linear(ed, h), nn.ReLU(), nn.Linear(h, input_dim)
        )

    def forward(self, x: torch.Tensor):
        z = self.encoder(x)
        recon = self.decoder(z)
        return z, recon

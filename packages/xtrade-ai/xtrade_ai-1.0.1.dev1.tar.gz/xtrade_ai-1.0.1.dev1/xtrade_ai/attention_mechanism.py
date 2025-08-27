"""
XTrade-AI Attention Mechanism Module

Provides transformer and attention components for deep learning models.
"""

import math
from typing import Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F


class MultiHeadAttention(nn.Module):
    """Multi-head attention mechanism"""

    def __init__(self, d_model: int, num_heads: int, dropout: float = 0.1):
        """Initialize multi-head attention

        Args:
            d_model: Model dimension
            num_heads: Number of attention heads
            dropout: Dropout rate
        """
        super().__init__()
        assert d_model % num_heads == 0

        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads

        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)

        self.dropout = nn.Dropout(dropout)

    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        mask: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass

        Args:
            query: Query tensor (batch_size, seq_len, d_model)
            key: Key tensor (batch_size, seq_len, d_model)
            value: Value tensor (batch_size, seq_len, d_model)
            mask: Optional mask tensor

        Returns:
            Output tensor and attention weights
        """
        batch_size = query.size(0)
        seq_len = query.size(1)

        # Linear transformations and split into heads
        Q = (
            self.W_q(query)
            .view(batch_size, seq_len, self.num_heads, self.d_k)
            .transpose(1, 2)
        )
        K = (
            self.W_k(key)
            .view(batch_size, seq_len, self.num_heads, self.d_k)
            .transpose(1, 2)
        )
        V = (
            self.W_v(value)
            .view(batch_size, seq_len, self.num_heads, self.d_k)
            .transpose(1, 2)
        )

        # Attention scores
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)

        # Apply mask if provided
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)

        # Attention weights
        attention_weights = F.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)

        # Apply attention to values
        context = torch.matmul(attention_weights, V)

        # Concatenate heads
        context = (
            context.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)
        )

        # Final linear transformation
        output = self.W_o(context)

        return output, attention_weights


class PositionwiseFeedForward(nn.Module):
    """Position-wise feed-forward network"""

    def __init__(self, d_model: int, d_ff: int, dropout: float = 0.1):
        """Initialize feed-forward network

        Args:
            d_model: Model dimension
            d_ff: Feed-forward dimension
            dropout: Dropout rate
        """
        super().__init__()
        self.fc1 = nn.Linear(d_model, d_ff)
        self.fc2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)
        self.activation = nn.ReLU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass

        Args:
            x: Input tensor (batch_size, seq_len, d_model)

        Returns:
            Output tensor
        """
        x = self.fc1(x)
        x = self.activation(x)
        x = self.dropout(x)
        x = self.fc2(x)
        return x


class TransformerBlock(nn.Module):
    """Transformer encoder block"""

    def __init__(self, d_model: int, num_heads: int, d_ff: int, dropout: float = 0.1):
        """Initialize transformer block

        Args:
            d_model: Model dimension
            num_heads: Number of attention heads
            d_ff: Feed-forward dimension
            dropout: Dropout rate
        """
        super().__init__()

        self.attention = MultiHeadAttention(d_model, num_heads, dropout)
        self.norm1 = nn.LayerNorm(d_model)
        self.dropout1 = nn.Dropout(dropout)

        self.ff = PositionwiseFeedForward(d_model, d_ff, dropout)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout2 = nn.Dropout(dropout)

    def forward(
        self, x: torch.Tensor, mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """Forward pass

        Args:
            x: Input tensor (batch_size, seq_len, d_model)
            mask: Optional mask tensor

        Returns:
            Output tensor
        """
        # Self-attention with residual connection
        attn_output, _ = self.attention(x, x, x, mask)
        x = self.norm1(x + self.dropout1(attn_output))

        # Feed-forward with residual connection
        ff_output = self.ff(x)
        x = self.norm2(x + self.dropout2(ff_output))

        return x


class PositionalEncoding(nn.Module):
    """Positional encoding for transformer models"""

    def __init__(self, d_model: int, max_len: int = 5000):
        """Initialize positional encoding

        Args:
            d_model: Model dimension
            max_len: Maximum sequence length
        """
        super().__init__()

        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)

        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model)
        )

        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)

        pe = pe.unsqueeze(0).transpose(0, 1)
        self.register_buffer("pe", pe)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Add positional encoding to input

        Args:
            x: Input tensor (seq_len, batch_size, d_model)

        Returns:
            Tensor with positional encoding added
        """
        x = x + self.pe[: x.size(0), :]
        return x


class SelfAttentionPooling(nn.Module):
    """Self-attention pooling for sequence aggregation"""

    def __init__(self, input_dim: int):
        """Initialize self-attention pooling

        Args:
            input_dim: Input dimension
        """
        super().__init__()
        self.attention_weights = nn.Linear(input_dim, 1)

    def forward(
        self, x: torch.Tensor, mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """Forward pass

        Args:
            x: Input tensor (batch_size, seq_len, input_dim)
            mask: Optional mask tensor

        Returns:
            Pooled tensor (batch_size, input_dim)
        """
        # Calculate attention scores
        scores = self.attention_weights(x).squeeze(-1)  # (batch_size, seq_len)

        # Apply mask if provided
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)

        # Calculate attention weights
        weights = F.softmax(scores, dim=-1)  # (batch_size, seq_len)

        # Apply attention weights
        weighted = x * weights.unsqueeze(-1)  # (batch_size, seq_len, input_dim)

        # Sum over sequence dimension
        output = weighted.sum(dim=1)  # (batch_size, input_dim)

        return output


class CrossAttention(nn.Module):
    """Cross-attention mechanism for attending between different sequences"""

    def __init__(self, d_model: int, num_heads: int, dropout: float = 0.1):
        """Initialize cross-attention

        Args:
            d_model: Model dimension
            num_heads: Number of attention heads
            dropout: Dropout rate
        """
        super().__init__()
        self.multihead_attn = MultiHeadAttention(d_model, num_heads, dropout)

    def forward(
        self,
        query: torch.Tensor,
        context: torch.Tensor,
        mask: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass

        Args:
            query: Query sequence (batch_size, query_len, d_model)
            context: Context sequence (batch_size, context_len, d_model)
            mask: Optional mask tensor

        Returns:
            Output tensor and attention weights
        """
        return self.multihead_attn(query, context, context, mask)


class TemporalAttention(nn.Module):
    """Temporal attention for time series data"""

    def __init__(self, input_dim: int, hidden_dim: int, num_heads: int = 4):
        """Initialize temporal attention

        Args:
            input_dim: Input dimension
            hidden_dim: Hidden dimension
            num_heads: Number of attention heads
        """
        super().__init__()

        self.input_projection = nn.Linear(input_dim, hidden_dim)
        self.attention = MultiHeadAttention(hidden_dim, num_heads)
        self.output_projection = nn.Linear(hidden_dim, input_dim)

        # Learnable temporal encoding
        self.temporal_encoding = nn.Parameter(torch.randn(1, 1000, hidden_dim))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass

        Args:
            x: Input tensor (batch_size, seq_len, input_dim)

        Returns:
            Output tensor with temporal attention applied
        """
        batch_size, seq_len, _ = x.shape

        # Project input
        x = self.input_projection(x)

        # Add temporal encoding
        x = x + self.temporal_encoding[:, :seq_len, :]

        # Apply attention
        attended, _ = self.attention(x, x, x)

        # Project back to input dimension
        output = self.output_projection(attended)

        return output


class AdaptiveAttention(nn.Module):
    """Adaptive attention that adjusts based on input characteristics"""

    def __init__(self, input_dim: int, num_heads: int = 8):
        """Initialize adaptive attention

        Args:
            input_dim: Input dimension
            num_heads: Number of attention heads
        """
        super().__init__()

        self.num_heads = num_heads
        self.attention_modules = nn.ModuleList(
            [MultiHeadAttention(input_dim, heads) for heads in [2, 4, 8]]
        )

        # Gating network to select attention module
        self.gate = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, len(self.attention_modules)),
            nn.Softmax(dim=-1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass

        Args:
            x: Input tensor (batch_size, seq_len, input_dim)

        Returns:
            Output tensor with adaptive attention
        """
        # Calculate gating weights based on input
        gate_input = x.mean(dim=1)  # Global average pooling
        gate_weights = self.gate(gate_input)  # (batch_size, num_modules)

        # Apply each attention module
        outputs = []
        for module in self.attention_modules:
            output, _ = module(x, x, x)
            outputs.append(output)

        # Stack outputs
        stacked_outputs = torch.stack(
            outputs, dim=1
        )  # (batch_size, num_modules, seq_len, input_dim)

        # Apply gating weights
        gate_weights = gate_weights.unsqueeze(-1).unsqueeze(
            -1
        )  # (batch_size, num_modules, 1, 1)
        weighted_output = (stacked_outputs * gate_weights).sum(dim=1)

        return weighted_output

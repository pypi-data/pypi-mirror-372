# Data Pipeline & Leakage Prevention

This guide covers end-to-end data flow: sourcing, resampling, alignment, scaling, splitting, and evaluation without leakage.

## Overview

1. Ingest raw OHLCV per symbol/timeframe
2. Resample/aggregate to desired timeframes
3. Engineer indicators per timeframe
4. Align (join) multi-timeframe features to base index
5. Split into train/validation/test
6. Fit scalers on train only; transform val/test
7. Build numpy arrays and feed to environment

## Resampling & Alignment

```python
# Example using pandas
base = df_1h  # base timeframe (1h)
h4  = df_raw.resample('4H').agg({'open':'first','high':'max','low':'min','close':'last','volume':'sum'})

# Indicators per TF
ind_1h = build_indicators(base)
ind_4h = build_indicators(h4)

# Align to base index
ind_4h = ind_4h.reindex(base.index).ffill()

# Concatenate features
features = np.column_stack([ind_1h.values, ind_4h.values]).astype('float32')
ohlcv    = base[['open','high','low','close','volume']].values.astype('float32')
```

## Splitting & Scaling

```python
from xtrade_ai.data_preprocessor import DataPreprocessor

N = len(ohlcv)
train_idx = int(N*0.8)

pre = DataPreprocessor(cfg)
pre.fit(ohlcv[:train_idx], features[:train_idx])
train = pre.transform(ohlcv[:train_idx], features[:train_idx])
val   = pre.transform(ohlcv[train_idx:], features[train_idx:])
```

Guidelines:
- Never call `.fit()` on validation/test.
- Optionally use rolling/walk-forward splits for time series.
- Ensure no future information leaks (no shifts that peek ahead).

## Walk-Forward Validation

```python
def rolling_windows(X_ohlcv, X_ind, window=0.6, step=0.1):
	N = len(X_ohlcv)
	train_len = int(N*window)
	k = int(N*step)
	start = 0
	while start+train_len < N:
		yield slice(0, start+train_len), slice(start+train_len, min(N, start+train_len+k))
		start += k
```

## Evaluation Mode

- Use `modules.environment_setup.build_env(..., session_type='evaluation')` to avoid fitting.
- Or reuse a persisted `DataPreprocessor` fitted on train (if you serialize your own preprocessing pipeline).

## Common Pitfalls

- Mismatched indices across timeframes → misaligned features.
- Leakage via global scaler fit on full dataset.
- Including future candles or higher-TF bars not available at time t.

## Best Practices

- Keep a canonical base timeframe; reindex all others.
- Validate shapes and NaN handling after joins.
- Log feature stats on train vs val to detect drift/leakage.

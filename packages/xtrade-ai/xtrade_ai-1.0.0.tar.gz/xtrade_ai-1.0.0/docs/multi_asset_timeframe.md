# Multi-Asset and Multi-Timeframe Design

This guide details patterns to handle multiple symbols and multiple timeframes safely and efficiently with XTrade-AI.

## Philosophy

- Framework is data-agnostic; you bring OHLCV + indicators in any structure.
- Symbols/timeframes belong to your data layer. Training remains broker-neutral and avoids coupling.

## Patterns

### 1) One-Env-Per-(Symbol, Timeframe) (Recommended)

- Create a separate `XTradeEnvironment` per pair `(symbol, timeframe)`.
- Train one SB3 model per pair. Run in parallel with SB3 VecEnv or via multiprocessing.

Pros: simple, no shape explosion, clear model-per-market granularity.
Cons: more models to manage.

```python
from stable_baselines3.common.vec_env import DummyVecEnv

pairs = [("BTCUSDT","1h"), ("ETHUSDT","1h"), ("BTCUSDT","4h")]

envs = []
for sym, tf in pairs:
	ohlcv, ind = load_prepared(sym, tf)
	envs.append(lambda sym=sym, tf=tf, ohlcv=ohlcv, ind=ind: XTradeEnvironment(cfg, ohlcv, ind))

vec = DummyVecEnv(envs)
fw = XTradeAIFramework(cfg)
fw.sb3.create("A2C", vec)
fw.sb3.train(total_timesteps=200_000)
# Or iterate per-env and train/save per pair
```

### 2) Single Env, Multi-Channel Features

- Concatenate features across timeframes/symbols as extra columns in `technical_indicators`.
- Keep per-feature naming and consistent order.

Pros: single model learns cross-timeframe/symbol signals.
Cons: larger observations; careful scaling and leakage control.

```python
# Example: add H1 and H4 indicators to same row
ind_base = build_indicators(base_tf_df)
ind_h4   = build_indicators(h4_df).reindex(base_tf_df.index).ffill()
features = np.column_stack([ind_base.values, ind_h4.values])
env = XTradeEnvironment(cfg, ohlcv_base.values, features.astype('float32'))
```

## Data Preparation

- Resample to desired timeframes (e.g., Pandas `.resample('4H')`).
- Align all timeframes to the base index (e.g., 1h); forward-fill gaps.
- Ensure scalers fit only on training split to prevent leakage.

```python
# Train/val split
train_idx = int(len(df)*0.8)
pre.fit(ohlcv[:train_idx], features[:train_idx])
train_data = pre.transform(ohlcv[:train_idx], features[:train_idx])
val_data   = pre.transform(ohlcv[train_idx:], features[train_idx:])
```

## Model Registry and Folders

- Save per (symbol, agent, timeframe) as preferred by your ops [[memory:4852136]].
- Example structure:

```
models/
  BTCUSDT/
    A2C/
      1h/
        run_2025-08-25.models
  ETHUSDT/
    PPO/
      4h/
        run_2025-08-25.models
```

## Cross-Symbol Features (Optional)

- For pair-trading or basket features, include spread/ratio features into indicators.
- Example: `ratio = price_SYM1 / price_SYM2`; make sure alignment and scaling are correct.

## Evaluation and Leakage

- In evaluation, use `session_type='evaluation'` in the environment builder to only transform.
- Never concatenate future bars from higher TF into the current step.
- Align features so that each row uses only data available at that timestamp.

## Deployment Strategies

- Per-market model routing: route symbol/timeframe to its corresponding model.
- Unified model: single policy handling all with feature flags for symbol/timeframe.
- Hybrid: cluster markets with similar regimes, share a model per cluster.

## Tips

- Keep observation size manageable; prune non-informative features.
- Verify stationarity and consistent scaling across assets.
- Validate with walk-forward splits per symbol/timeframe.

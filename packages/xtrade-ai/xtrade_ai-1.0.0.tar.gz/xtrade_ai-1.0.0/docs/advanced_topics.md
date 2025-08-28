# Advanced Topics

This page covers advanced techniques to push the framework further.

## Hyperparameter Optimization (HPO)

- Use the simple utilities in `modules/optimization.py` (`grid_search`, `random_search`) or integrate Optuna.
- Tune SB3 parameters from `config.get_algorithm_config()`, e.g. `ppo_n_steps`, `batch_size`, `clip_range`.

```python
from xtrade_ai.modules.optimization import grid_search

space = {
	"ppo_n_steps": [512, 1024, 2048],
	"ppo_clip_range": [0.1, 0.2, 0.3],
}

def objective(params):
	cfg.training.ppo_n_steps = params["ppo_n_steps"]
	cfg.training.ppo_clip_range = params["ppo_clip_range"]
	fw = XTradeAIFramework(cfg)
	fw.train(env, algorithm='PPO', total_timesteps=100_000)
	return fw.get_training_metrics()["win_rate"]

best = grid_search(space, objective)
```

## Calibration & Ensemble

- `modules/calibration.py`:
  - `TemperatureScaler` for logits
  - `EnsembleCalibrator` to learn weights combining policy vs TA signals
- Fit on validation set only. Apply weights during `ActionSelector.select` via `ensemble_weights`.

## Distributed & Parallel Training

- SB3 supports VecEnv; for more scale, use Ray actors to train per (symbol, timeframe) in parallel.
- Keep reproducibility: set seeds, log versions, pin dependency ranges.

## Policy Validation

- Use `modules/policy_validator.py` to verify observation/action spaces and basic sanity checks before training.
- Validate observation shapes per environment to avoid silent broadcasting errors.

## Security & Persistence

- Model bundles are encrypted with AES-256 using `cryptography`. Prefer password-based KDF in production.
- Rotate `.key` files and restrict filesystem permissions (umask/ACL).

## Live Trading Considerations

- Add a broker adapter (e.g., MetaTrader5, Binance) in a separate client layer.
- Throttle API calls, implement circuit breakers, and add risk hard-limits.
- Monitor latency and slippage; log fills and rejects in `MonitoringModule`.

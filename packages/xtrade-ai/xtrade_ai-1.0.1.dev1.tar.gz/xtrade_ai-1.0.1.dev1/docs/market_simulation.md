# Market Simulation & Meta-Learning

Enable simulated regimes to augment training for meta-learning.

## Config
```python
cfg.environment.enable_market_simulation = True
cfg.environment.simulation_regimes = ['trending','ranging','volatile','quiet']
cfg.environment.simulation_multiplier = 2
```

## Run
```python
from modules.environment_setup import build_env
reports = framework.simulate_and_train_or_evaluate(
    environment_builder=build_env,
    ohlcv=ohlcv_original,
    indicators=indicators_original,
    algorithm='PPO',
    total_timesteps=10000,
    mode='train'
)
```

## Reports
- `simulated_reports`: per regime, list of monitoring exports
- `original_report`: monitoring export for original data
- `comparison`: per-action mean, reward distribution mean, penalty means, performance means vs original

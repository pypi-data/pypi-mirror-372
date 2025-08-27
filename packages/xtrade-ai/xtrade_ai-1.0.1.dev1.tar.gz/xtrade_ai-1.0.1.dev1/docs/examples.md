# Examples

## Multi-Order Open
```python
cfg.trading.orders_per_action = 3
```

## Targeted Close
```python
# close positions at indices 0 and 2 on next CLOSE action
env.set_close_indices([0,2])
```

## Run Simulation + Training + Comparison
```python
from modules.environment_setup import build_env
cfg.environment.enable_market_simulation = True
reports = framework.simulate_and_train_or_evaluate(
    environment_builder=build_env,
    ohlcv=ohlcv_original,
    indicators=indicators_original,
    algorithm='PPO',
    total_timesteps=10000,
)
print(reports['comparison']['original'])
```

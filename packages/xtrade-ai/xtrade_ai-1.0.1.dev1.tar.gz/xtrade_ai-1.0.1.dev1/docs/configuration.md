# Configuration

`config.py` defines structured configuration via dataclasses:
- `ModelConfig`: model hyperparameters (state_dim, hidden_dim, num_heads, learning_rate, etc.)
- `TradingConfig`: trading constraints (max_positions, orders_per_action, stop_loss, take_profit, commission_rate, slippage)
- `EnvironmentConfig`: environment settings (window_size, rewards shaping weights, simulation flags)
- `TrainingConfig`: SB3 hyperparameters per algorithm (PPO/A2C/DQN/SAC/TD3/TRPO/QRDQN)
- `TechnicalIndicatorConfig`: indicator parameters

## Key Options
- Reward shaping: `pnl_weight`, `close_rule_weight`, `risk_penalty_weight`, `cost_weight`, `drawdown_penalty_weight`, `volatility_penalty_weight`, `reward_scale`
- Market Simulation: `enable_market_simulation`, `simulation_regimes`, `simulation_multiplier`, `simulation_drift_range`, `simulation_vol_multipliers`
- Trading: `orders_per_action`, `max_positions`, `risk_tolerance`, `max_drawdown`

## Example
```python
from config import XTradeAIConfig
cfg = XTradeAIConfig()
cfg.environment.enable_market_simulation = True
cfg.trading.orders_per_action = 3
cfg.environment.pnl_weight = 0.6
```

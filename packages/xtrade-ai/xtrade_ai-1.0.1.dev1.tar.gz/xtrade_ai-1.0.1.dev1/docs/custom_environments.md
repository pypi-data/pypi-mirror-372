# Building Custom Environments

This guide explains how to create your own Gymnasium-compatible environment that works with the XTrade-AI framework.

## Requirements

- Inherit from `gymnasium.Env`
- Implement `__init__`, `reset`, `step` methods
- Define `action_space` and `observation_space`
- Produce observations compatible with your chosen policy/state design

You can use `xtrade_ai.XTradeEnvironment` as a reference implementation.

## Minimal Template

```python
import gymnasium as gym
import numpy as np
from gymnasium import spaces

class MyTradingEnv(gym.Env):
	metadata = {"render_modes": ["human"], "render_fps": 2}

	def __init__(self, config, ohlcv_data, indicators=None, render_mode=None, monitor=None):
		self.config = config
		self.ohlcv = np.asarray(ohlcv_data, dtype=np.float32)
		self.indicators = np.asarray(indicators or np.zeros((len(self.ohlcv), 0), dtype=np.float32), dtype=np.float32)
		self.window_size = self.config.environment.window_size
		self.max_steps = self.config.environment.max_episode_steps
		self.current_step = 0
		self.balance = self.config.trading.initial_balance
		self.equity = self.balance
		self.positions = []
		self.monitor = monitor  # optional

		# Define spaces
		obs_dim = self.window_size * self.ohlcv.shape[1] + self.indicators.shape[1] + 8 + 4
		self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(obs_dim,), dtype=np.float32)
		self.action_space = spaces.Discrete(4)  # BUY, SELL, HOLD, CLOSE

	def reset(self, *, seed=None, options=None):
		super().reset(seed=seed)
		self.current_step = self.window_size
		self.balance = self.config.trading.initial_balance
		self.equity = self.balance
		self.positions.clear()
		return self._get_observation(), {}

	def step(self, action: int):
		# 1) Apply action (open/close/hold), update balance/positions
		# 2) Advance time, compute pnl and reward
		self.current_step += 1
		done = self.current_step >= min(self.max_steps, len(self.ohlcv))
		reward = 0.0
		info = {}
		return self._get_observation(), reward, bool(done), False, info

	def _get_observation(self):
		start = max(0, self.current_step - self.window_size)
		end = self.current_step
		win = self.ohlcv[start:end]
		if win.shape[0] < self.window_size:
			pad = np.zeros((self.window_size - win.shape[0], self.ohlcv.shape[1]), dtype=np.float32)
			win = np.vstack([pad, win])
		ind_row = self.indicators[min(end - 1, self.indicators.shape[0] - 1)] if self.indicators.size else np.zeros((0,), dtype=np.float32)
		market_state = np.zeros((8,), dtype=np.float32)
		account = np.array([self.balance, self.equity, 0.0, self.balance], dtype=np.float32)
		return np.concatenate([win.flatten(), ind_row.flatten(), market_state, account], dtype=np.float32)
```

## Integration with XTrade-AI

Use your custom environment directly with `XTradeAIFramework` and SB3 algorithms.

```python
from xtrade_ai import XTradeAIConfig, XTradeAIFramework
from my_env import MyTradingEnv

cfg = XTradeAIConfig()
ohlcv, indicators = ...  # preprocessed arrays
env = MyTradingEnv(cfg, ohlcv, indicators)
fw = XTradeAIFramework(cfg)
fw.train(environment=env, algorithm='PPO', total_timesteps=50_000)
```

## Using the Environment Builder

If you want the framework to handle preprocessing and monitoring automatically, follow the pattern in `modules/environment_setup.py`:

```python
from xtrade_ai.modules.environment_setup import build_env
cfg = XTradeAIConfig()
env = build_env(cfg, ohlcv, indicators, session_type='training')
```

- `session_type='training'` will fit scalers; `'evaluation'` will only transform (prevents leakage).

## Custom Reward Shaping

- You can embed `RewardShaper` (`xtrade_ai.modules.reward_shaping.RewardShaper`) in your env to compute richer rewards using config weights: `cost_weight`, `drawdown_penalty_weight`, `volatility_penalty_weight`.
- Update equity each step using `reward_shaper.update_equity(equity)` to enable drawdown/volatility penalties.

## Multi-Order and Targeted Close

- Provide actions mapping and manage positions list in the environment.
- To support targeted close, expose a method like `set_close_indices(indices: List[int])` and consume it on CLOSE action.

## Tips

- Ensure observation shape stays constant across steps.
- Keep `step` side effects deterministic given state and action.
- Validate `action_space.contains(action)` and clip/guard quantities.
- Log per-step metrics via a monitoring module if needed.

## Validation Checklist

- Observation and action spaces defined and stable
- `reset()` returns `(obs, info)` and resets episode state
- `step()` returns `(obs, reward, terminated, truncated, info)`
- No in-place fitting in evaluation mode (avoid data leakage)
- Compatible with SB3’s vectorized wrappers (no stateful global singletons)

# Quickstart

## Example CLI
```bash
python clients/vendor/xtrade-ai/example_usage.py --algo PPO --timesteps 20000 --save
```

## Minimal Programmatic Use
```python
import numpy as np
from xtrade_ai_framework import XTradeAIFramework
from config import XTradeAIConfig

cfg = XTradeAIConfig()
fw = XTradeAIFramework(cfg)

ohlcv = np.random.rand(512,5).astype('float32')
inds = np.random.rand(512,8).astype('float32')

from modules.environment_setup import build_env
env = build_env(cfg, ohlcv, inds, session_type='training')
fw.train(environment=env, algorithm='PPO', total_timesteps=10000)

decision = fw.predict(ohlcv=ohlcv[-60:], indicators=inds[-60:])
print(decision.action.name, decision.position_size, decision.confidence)
```

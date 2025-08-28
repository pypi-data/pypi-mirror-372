# Training & Fine-Tuning

## Training
```python
from modules.environment_setup import build_env
env = build_env(cfg, ohlcv, indicators, session_type='training')
framework.train(environment=env, algorithm='PPO', total_timesteps=100000)
```

## Fine-Tuning
```python
env = build_env(cfg, new_ohlcv, new_indicators, session_type='training')
framework.fine_tune(environment=env, algorithm='PPO', model_path='ppo_model.zip', total_timesteps=50000)
```

## Ensemble Weight Learning (Validation)
```python
# policy_conf, ta_conf, labels computed from validation set
weights = framework.fit_ensemble_weights(policy_conf, ta_conf, labels)
print(weights)  # {'policy': 0.6, 'ta': 0.4}
```

## Saving Models
```python
from utils.save_model import ModelSaver
saver = ModelSaver(encrypt=True, password='secret')
path = framework.save(saver, name='xtrade_ai_prod', extra_metadata={'run_id':'abc123'})
print('saved to', path)
```

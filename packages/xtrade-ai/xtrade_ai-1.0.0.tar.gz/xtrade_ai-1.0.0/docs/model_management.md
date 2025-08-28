# Model Management & Versioning

This guide shows how to save, organize, and fine-tune models produced by XTrade-AI.

## Saving with ModelSaver

```python
from xtrade_ai import XTradeAIConfig
from xtrade_ai.utils.save_model import ModelSaver
from xtrade_ai.xtrade_ai_framework import XTradeAIFramework

cfg = XTradeAIConfig()
fw  = XTradeAIFramework(cfg)
# ... train framework ...

saver = ModelSaver(config=cfg)
path = saver.save_framework(
	models=fw.get_all_models(),
	metadata=fw.export_metadata({"note":"experiment A"}),
	name="xtrade_ai_bundle"
)
print("saved to:", path)
```

- Uses `cfg.persistence` for `save_dir`, `encrypt_models`, `password`, and metadata inclusion.
- Produces an encrypted `.models` file (zip + AES-256). Key stored to `.key` if no password provided.

## Directory Convention

Recommended layout per operations policy [[memory:4852136]]:

```
models/
  SYMBOL/
    AGENT/
      TIMEFRAME/
        2025-08-25_120000.models
```

## Fine-Tuning SB3 Models

```python
# Save SB3-native model
sb3_model = fw.sb3.get_model()
sb3_model.save("/tmp/sb3_model.zip")

# Fine-tune
fw.fine_tune(environment=env, algorithm="A2C", model_path="/tmp/sb3_model.zip", total_timesteps=50_000)
```

- Fine-tune loads the model and continues learning without re-creating.
- XGBoost fit runs only if features+labels are provided explicitly.

## Loading Bundles

```python
from xtrade_ai.utils.save_model import ModelLoader
bundle = ModelLoader(password="optional").load_framework("path/to/file.models")
models = bundle['models']
meta   = bundle['metadata']
```

- SB3 policies are stored in their own format; the bundle tracks metadata and auxiliary modules.

## Metadata

- `export_metadata()` includes ensemble weights, calibration temperature, and config snapshot.
- You can add extra keys to tag experiments.

## Versioning Tips

- Prefer semantic naming: `algo_params`, `seed`, `data_span` in metadata.
- Use `cfg.save_config()` to persist config JSON alongside models.
- Keep changelogs in experiment trackers (TensorBoard/W&B/MLflow).

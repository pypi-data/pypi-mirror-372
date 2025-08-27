# API Reference

## XTradeAIFramework
- `train(environment, algorithm, total_timesteps, xgb_features=None, xgb_labels=None)`
- `fine_tune(environment, algorithm, model_path, total_timesteps, xgb_features=None, xgb_labels=None)`
- `predict(ohlcv, indicators, market_state=None, positions=None) -> TradingDecision`
- `fit_ensemble_weights(policy_conf, ta_conf, labels) -> dict`
- `save(saver, name='xtrade_ai_framework', extra_metadata=None) -> str`
- `simulate_and_train_or_evaluate(environment_builder, ohlcv, indicators, algorithm, total_timesteps, mode='train') -> dict`

## XTradeEnvironment
- `set_close_indices(indices: List[int])`
- Gym API: `reset()`, `step(action)`

## MonitoringModule
- `start_session(session_type, metadata=None)`
- `record_step(...)`, `record_trade_open(...)`, `record_trade_close(...)`, `record_episode(...)`
- `get_trading_performance() -> dict`, `export_json() -> dict`
- `plot_equity()`, `plot_rewards()`

## ModelSaver / ModelLoader
- `ModelSaver.save_framework(models: dict, metadata: dict, name='xtrade_ai_framework') -> str`
- `ModelLoader.load_framework(model_path: str) -> dict`

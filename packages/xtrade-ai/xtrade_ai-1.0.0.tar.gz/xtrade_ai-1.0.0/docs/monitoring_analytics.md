# Monitoring & Analytics

## MonitoringModule
- `record_step`, `record_trade_open/close`, `record_episode`
- `get_trading_performance()` returns performance metrics (Sharpe, MDD, win rate, etc.)
- `export_json()` returns a full report for analytics
- `plot_equity()`, `plot_rewards()` to visualize

## IntegratedAnalysis
```python
from modules.integrated_analysis import IntegratedAnalysis
report = monitor.export_json()
ia = IntegratedAnalysis(report)
print(ia.per_action_stats())
print(ia.reward_distribution())
print(ia.pseudo_confusion())
print(ia.step_mean('risk_penalty'))
```

## SB3 Callback (optional)
Use `monitor.get_sb3_callback()` if you want to attach a callback to SB3 training loops.

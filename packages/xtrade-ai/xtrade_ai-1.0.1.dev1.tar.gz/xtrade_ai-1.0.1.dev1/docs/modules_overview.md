# Modules Overview

- `baseline3_integration.py`: wrapper SB3/SB3-contrib (PPO, DQN, SAC, A2C, TD3, TRPO, QRDQN)
- `technical_analysis.py`: CNN-LSTM menghasilkan logits buy/sell/hold
- `close_order_decision.py`: Transformer memutuskan indeks posisi untuk ditutup
- `risk_management.py`: GRU menghitung risk score & penyesuaian ukuran posisi
- `technical_indicator.py`: Autoencoder indikator adaptif
- `xgboost_module.py`: fitur seleksi dan prediksi pendukung (opsional)
- `reward_shaping.py`: shaping berbasis pnl/close/risk + biaya/drawdown/vol
- `action_selector.py`: ensemble final; mendukung bobot ensemble tersimpan
- `monitoring.py`: rekam metrik, summary, plot; ekspor JSON
- `market_simulation.py`: generator OHLCV sintetis per regime
- `calibration.py`: Temperature/Platt scaling, EnsembleCalibrator
- `optimization.py`: grid/random search (stub)
- `policy_validator.py`: sanity checks
- `environment_setup.py`: builder env + preprocessor + monitoring

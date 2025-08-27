# Decision Making (Ensemble)

Dokumen ini menjelaskan bagaimana framework menggabungkan berbagai sinyal untuk menghasilkan aksi final.

## Sumber Sinyal

- RL Policy (SB3): aksi dan confidence dari model baseline (PPO/DQN/SAC/A2C/TD3/TRPO/QRDQN)
- Technical Analysis (CNN-LSTM): logits `[buy, sell, hold]`
- Close Decision (Transformer): indeks posisi untuk ditutup
- Risk Management (GRU): `risk_score` dan `position_size_adjustment`

## Proses Ensemble

- `modules/action_selector.py` menerima semua sinyal dan menghasilkan `TradingDecision`:
  - Jika `close_indices` ada → prioritas CLOSE (targeted jika diberikan)
  - Jika risiko tinggi → bias ke HOLD atau kecilkan ukuran
  - Gabungkan kebijakan RL dan TA dengan:
    - Confidence-based blending (default), atau
    - `ensemble_weights` hasil `EnsembleCalibrator.fit()` pada data validasi

## Kalibrasi

- `TemperatureScaler` untuk logits TA (menyetarakan calibration)
- `EnsembleCalibrator` mempelajari bobot antara policy vs TA dengan target label val

## Output Akhir

`TradingDecision`:
- `action`: BUY/SELL/HOLD/CLOSE (enum)
- `confidence`: skor 0..1
- `position_size`: proporsi relatif terhadap balance
- `close_indices`: (opsional) subset posisi untuk ditutup

## Praktik Terbaik

- Fit kalibrasi/bobot ensemble pada set validasi terpisah
- Logging keputusan dan metrik via `MonitoringModule` untuk audit
- Tambahkan aturan bisnis (circuit breakers, max exposure) di layer kontrol live

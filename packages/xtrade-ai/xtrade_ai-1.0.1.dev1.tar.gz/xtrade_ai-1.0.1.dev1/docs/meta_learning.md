# Meta Learning

Dokumen ini menjelaskan konsep meta learning dalam XTrade-AI: bagaimana framework beradaptasi cepat terhadap kondisi pasar baru melalui deteksi rezim dan simulasi pasar.

## Tujuan Meta Learning

- Mempercepat adaptasi model terhadap perubahan rezim (trending, ranging, volatile, quiet)
- Mengurangi overfitting terhadap satu domain pasar dengan variasi simulasi
- Menyediakan sinyal konteks (regime) untuk modul lain (risk, action selector)

## Komponen

- `modules/meta_learning.py`: LSTM-based market regime detector (bullish/bearish/neutral)
- `modules/market_simulation.py`: generator OHLCV sintetis untuk berbagai rezim
- `env`/`framework`: utilitas untuk menjalankan eksperimen multi-regime dan membandingkan hasil

## Alur Kerja

1) Siapkan data asli (OHLCV + indikator)
2) Aktifkan simulasi (opsional) melalui `EnvironmentConfig.enable_market_simulation`
3) Gunakan `XTradeAIFramework.simulate_and_train_or_evaluate(...)` untuk melatih/evaluasi pada data simulasi + data asli
4) Bandingkan metrik (Sharpe, MDD, win rate, penalti risiko/biaya/drawdown/volatilitas)

```python
reports = fw.simulate_and_train_or_evaluate(
	environment_builder=build_env,
	ohlcv=ohlcv,
	indicators=ind,
	algorithm='PPO',
	total_timesteps=200_000,
	mode='train',
)
```

## Deteksi Rezim Pasar

- `MetaLearning` (LSTM) dapat dilatih untuk mengklasifikasikan konteks pasar (bull/bear/neutral)
- Output rezim dapat dimasukkan sebagai fitur tambahan di observation atau bobot pada `ActionSelector`

## Simulasi Pasar

- `MarketSimulation` menyediakan data sintetis untuk rezim:
  - `trending`, `ranging`, `volatile`, `quiet`
- Parameter:
  - `simulation_multiplier`: berapa set per rezim
  - `simulation_drift_range`: rentang drift untuk trending
  - `simulation_vol_multipliers`: skala volatilitas

## Integrasi Keputusan

- Sinyal rezim dapat digunakan untuk:
  - Mengatur bobot ensemble (mis. saat trending, bobot TA trend-following ↑)
  - Menyesuaikan risk tolerance/position sizing
  - Mengubah kebijakan close (lebih agresif pada volatilitas tinggi)

## Evaluasi & Laporan

- `modules/integrated_analysis.py` menyusun diagnostik:
  - Per-action stats, distribusi reward, pseudo confusion
  - Rata-rata penalti risiko/biaya/drawdown/volatilitas
- Framework merata-ratakan per rezim sintetis dan membandingkannya dengan data asli

## Praktik Terbaik

- Gunakan validasi silang berbasis waktu (walk-forward) untuk menilai generalisasi lintas rezim
- Kalibrasi ulang ensemble weights per rezim bila perlu (fit di set validation)
- Hindari kebocoran: semua fitting (scaler, kalibrator, bobot ensemble) dilakukan pada data train/val yang tepat


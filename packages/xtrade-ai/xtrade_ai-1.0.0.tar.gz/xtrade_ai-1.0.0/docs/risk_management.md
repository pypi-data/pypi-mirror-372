# Risk Management

Dokumen ini menjelaskan cara framework melakukan manajemen risiko dan bagaimana modul risiko terintegrasi dalam alur keputusan.

## Tujuan

- Mengukur eksposur risiko saat ini (posisi, volatilitas, drawdown, biaya transaksi)
- Menentukan ukuran posisi (position sizing) yang aman
- Memberi sinyal pengurangan eksposur saat risiko tinggi

## Komponen Inti

- `modules/risk_management.py` (GRU-based): menghasilkan `RiskAssessment` berdasarkan fitur pasar dan posisi aktif.
- `modules/reward_shaping.py`: menghitung penalti risiko, biaya transaksi, drawdown, dan volatilitas untuk shaping reward.
- `base_environment.py`: menerapkan penalti tersebut pada reward setiap langkah.

## Fitur Masukan Risiko

- Fitur pasar: `[price, volume, bid, ask, spread, volatility, trend, momentum]`
- Ringkasan posisi: arah, entry, current price, qty, unrealized PnL, PnL% (disediakan env)

## Output Modul

`RiskAssessment`:
- `risk_score` (0..1): risiko relatif saat ini
- `position_size_adjustment`: faktor pengali ukuran posisi yang direkomendasikan

## Integrasi dalam Keputusan

- `XTradeAIFramework.predict()` memanggil `risk_module.assess(...)` dan meneruskan hasilnya ke `ActionSelector.select(...)`.
- `ActionSelector` dapat menurunkan confidence atau memilih HOLD bila `risk_score` tinggi.

## Reward Shaping dan Penalti

- `RewardShaper.update_equity(equity)` menyimpan ekuitas historis → menghitung drawdown & realized volatility.
- `compute(...)` menggabungkan komponen:
  - PnL delta
  - Bonus close
  - Penalti risiko (utilisasi posisi)
  - Penalti biaya (komisi dari notional)
  - Penalti drawdown
  - Penalti volatilitas
- Bobot dari `EnvironmentConfig`: `cost_weight`, `drawdown_penalty_weight`, `volatility_penalty_weight`.

## Position Sizing (Konfigurasi)

- `TradingConfig`: `min_position_size`, `max_position_size`, `risk_tolerance`.
- Anda dapat menambahkan logika sizing lanjutan di modul risiko untuk menyesuaikan `position_size_adjustment`.

## Praktik Terbaik

- Validasi `risk_score` di data validasi.
- Gunakan batasan risk hard-limit pada mode live (di luar framework ini, layer broker/controller).
- Monitor metrik risiko di `MonitoringModule` (drawdown, volatility).

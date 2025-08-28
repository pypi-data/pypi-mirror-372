# Technical Indicators

Dokumen ini menjelaskan bagaimana framework menangani indikator teknikal, mulai dari preprocessing hingga indikator adaptif berbasis autoencoder.

## Preprocessing Indikator

- Input: matriks indikator user `(N, K)` (mis. SMA, EMA, RSI, MACD, BB, ATR, dll).
- `DataPreprocessor`:
  - `handle_nan`: `pad` (default), `interpolate`, atau `drop`.
  - `fit_indicators()` pada data train, `transform_indicators()` pada val/test → mencegah leakage.

```python
pre.fit(ohlcv_train, indicators_train)
train = pre.transform(ohlcv_train, indicators_train)
val   = pre.transform(ohlcv_val, indicators_val)
```

## Indikator Multi-Timeframe

- Resample TF yang lebih tinggi, hitung indikator, `reindex` ke indeks TF dasar, `ffill`.
- Gabungkan kolom indikator lintas TF dalam `technical_indicators`.

## Adaptive Indicators (Autoencoder)

- `modules/technical_indicator.py`: autoencoder membuat representasi indikator yang lebih kompak/adaptif.
- Tujuan: mereduksi noise/dimensi dan menangkap struktur laten.

Pipeline contoh:
1) Siapkan `technical_indicators` standar (user-defined).
2) Latih autoencoder pada train split (opsional, offline).
3) Gunakan embedding/rekonstruksi sebagai fitur tambahan.

## Praktik Terbaik

- Standardisasi indikator numerik; batasi range dan outliers.
- Hindari memuat informasi masa depan (jangan gunakan future candle untuk bar saat ini).
- Dokumentasikan daftar indikator dan parameternya untuk replikasi.

# Technical Analysis (CNN-LSTM)

Dokumen ini menjelaskan modul Technical Analysis yang menghasilkan sinyal buy/sell/hold berbasis pola waktu.

## Arsitektur

- `modules/technical_analysis.py`: model CNN-LSTM:
  - `Conv1D` untuk ekstraksi fitur lokal dari sekuens harga/indikator
  - `LSTM` (2-layer) untuk menangkap dependensi temporal
  - Head linear untuk 3 kelas: `[buy, sell, hold]`

## Input

- Secara default contoh sederhana mengambil kanal OHLCV tertentu, mis. `close` dalam window `sequence_length` dari `config.model.sequence_length`.
- Anda dapat memperluas menjadi multi-channel (OHLCV + indikator) dengan menyesuaikan modul.

## Output

- Logits 3-dimensi, dapat diproses dengan softmax atau temperature scaling.
- Framework menerapkan `TemperatureScaler` (bila telah fit) sebelum ensemble.

## Integrasi

- Dipanggil pada inferensi di `XTradeAIFramework.predict()` untuk melengkapi sinyal kebijakan RL.
- Hasil logits diteruskan ke `ActionSelector.select(...)` bersama sinyal RL dan risiko.

## Pelatihan

- Contoh repos ini fokus pada RL sebagai penggerak utama; pelatihan TA dapat dilakukan offline:
  1) Labelkan data (mis. naik/turun/diam berdasarkan threshold return masa depan yang tidak overlapped)
  2) Bagi train/val, fit scaler pada train
  3) Latih CNN-LSTM dengan cross-entropy
  4) Simpan checkpoint dan muat saat inference

## Praktik Terbaik

- Hindari leakage saat pelabelan: gunakan horizon ke depan tanpa overlap informasi ke input.
- Pastikan window input konsisten dan tidak menyertakan bar masa depan.
- Evaluasi akurasi/ROC/PR pada val sebelum digunakan dalam ensemble.

# Mengapa Tidak Hanya SB3? Alasan Menggunakan Ensemble Semua Modul DL

Dokumen ini menjelaskan alasan arsitektural mengapa framework tidak sepenuhnya mengandalkan model SB3 (baseline RL) sebagai satu-satunya sumber keputusan, melainkan menggabungkannya dengan modul DL lain (Technical Analysis, Close Decision, Risk Management, Adaptive Indicators) melalui proses ensemble.

## Keterbatasan SB3-Only

- Single-objective: Reward tunggal sulit menangkap tujuan multi-kriteria (PnL, risiko, biaya, stabilitas) secara eksplisit.
- Partial observability: Kebijakan RL mungkin tidak sensitif terhadap pola mikro/struktural yang ditangkap oleh CNN/LSTM khusus.
- Data regime shift: RL dapat overfit ke satu rezim; modul terpisah (detektor rezim/TA) meningkatkan robustness.
- Interpretasi & kontrol: Risk constraints, targeted close, dan aturan bisnis lebih mudah dipaksakan di luar policy RL.

## Keunggulan Ensemble Multi-Modul

- Redundansi sumber sinyal: RL policy + TA logits + RiskAssessment + CloseDecision → keputusan lebih stabil.
- Kalibrasi: `TemperatureScaler` menyeimbangkan confidence TA; `EnsembleCalibrator` belajar bobot gabungan berdasarkan validasi.
- Kontrol risiko terpisah: Risk module dapat menurunkan ukuran posisi atau memaksa HOLD terlepas dari sinyal RL.
- Aksi struktural: Targeted close tak selalu “alami” bagi policy umum; modul khusus menanganinya.

## Implementasi di Framework

- `Baseline3Integration` menyediakan aksi utama dari policy RL.
- `TechnicalAnalysis` memberikan logits pola harga (buy/sell/hold).
- `CloseOrderDecision` menentukan indeks posisi untuk ditutup (prioritas saat tersedia).
- `RiskManagement` menghasilkan `risk_score` dan `position_size_adjustment`.
- `ActionSelector` menggabungkan semua sinyal dengan blending/weights untuk aksi final.

## Kalibrasi & Validasi

- Bobot ensemble dipelajari pada set validasi (bukan train) untuk mencegah kebocoran.
- Monitoring menangkap metrik per modul guna audit (Sharpe, MDD, distribusi reward).

## Dampak Operasional

- Robustness meningkat pada kondisi pasar berubah-ubah.
- Fleksibilitas: Anda dapat mengganti/mematikan modul tanpa retrain RL penuh.
- Observabilitas: Keputusan dapat diurai komponen penyusunnya (policy vs TA vs risiko).

## Kapan SB3-Only Cukup?

- Use-case sangat sederhana, data homogen, dan biaya serta risiko tidak dominan.
- Namun, bahkan pada kasus ini, modul risiko minimal tetap disarankan untuk guardrails.

## Ringkasan

Menggabungkan SB3 dengan modul DL khusus memberikan keseimbangan antara pembelajaran kebijakan jangka panjang dan sinyal domain-spesifik, sekaligus menyediakan kontrol risiko yang lebih baik serta kemampuan targeted actions seperti close order selektif. Ensemble bukan menggantikan RL, tetapi memperkuatnya di area yang secara praktis penting dalam trading nyata.

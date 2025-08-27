# Close Order Decision (Transformer)

Dokumen ini menjelaskan modul Close Order Decision berbasis Transformer untuk menentukan posisi mana yang sebaiknya ditutup.

## Tujuan

- Mengidentifikasi posisi yang layak ditutup berdasarkan profil PnL dan konteks pasar
- Mendukung targeted close (menutup subset posisi dengan indeks tertentu)

## Arsitektur

- `modules/close_order_decision.py`:
  - Encoder Transformer memproses fitur posisi (arah, entry, price, qty, pnl, pnl%) sebagai sekuens
  - Head sigmoid menghasilkan probabilitas `should_close` per posisi

## Input

- Daftar posisi `Position` dari environment (maks `trading.max_positions`)
- Fitur dapat diperluas (mis. durasi holding, volatilitas saat entry)

## Output

- `CloseOrderDecision` berisi:
  - `should_close`: bool umum (mis. ada posisi yang layak ditutup)
  - `close_indices`: list indeks posisi yang direkomendasikan untuk ditutup

## Integrasi dengan Environment

- `base_environment.py` menyediakan:
  - `set_close_indices(indices)` untuk menerima daftar indeks dari modul
  - Saat action `CLOSE`, env menutup `indices` jika tersedia; jika tidak ada, fallback menutup posisi profitable

## Praktik Terbaik

- Prioritaskan posisi dengan PnL negatif memburuk/drawdown tinggi untuk risk control, atau posisi profit dengan target tercapai
- Validasi precision/recall pada data validasi untuk threshold close
- Batasi jumlah close per langkah jika biaya transaksi tinggi

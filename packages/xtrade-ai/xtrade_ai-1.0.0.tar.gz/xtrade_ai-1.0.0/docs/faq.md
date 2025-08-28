# FAQ

### Apakah framework ini bisa tanpa GPU?
Bisa. Semua komponen berjalan di CPU, walau training akan lebih cepat dengan GPU.

### Bagaimana menghindari data leakage saat preprocessing?
Gunakan `DataPreprocessor.fit(...)` di data training saja, dan `transform(...)` untuk validasi/inferensi. Builder `environment_setup.build_env` sudah menerapkan pola ini.

### Bagaimana menyimpan model secara aman?
Gunakan `ModelSaver` dengan enkripsi (`encrypt=True`) dan password. File output `.models` berisi zip terenkripsi berikut metadata.

### Bagaimana menyesuaikan reward shaping?
Ubah bobot di `EnvironmentConfig` (`pnl_weight`, `risk_penalty_weight`, `cost_weight`, dsb.).

### Bagaimana mengaktifkan market simulation?
Set `cfg.environment.enable_market_simulation = True` lalu gunakan `simulate_and_train_or_evaluate`.

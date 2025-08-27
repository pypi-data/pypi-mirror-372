# XTrade-AI Test Suite

Test suite komprehensif untuk framework XTrade-AI, khususnya untuk testing training dan fine-tuning functionality.

## 📋 Overview

Test suite ini mencakup:

- **Training Tests**: Testing model training dengan berbagai algoritma dan konfigurasi
- **Fine-tuning Tests**: Testing fine-tuning dan transfer learning
- **Integration Tests**: Testing end-to-end workflow
- **Test Runner**: Script untuk menjalankan semua test dengan reporting

## 🏗️ Struktur Test

```
test/
├── test_training.py          # Training functionality tests
├── test_fine_tuning.py       # Fine-tuning functionality tests
├── test_integration.py       # Integration tests
├── test_runner.py           # Test runner script
├── README.md                # Dokumentasi ini
└── [existing test files]    # Test files yang sudah ada
```

## 🚀 Cara Menjalankan Tests

### 1. Menjalankan Semua Tests

```bash
# Dari root directory
python test/test_runner.py

# Atau dengan verbose output
python test/test_runner.py --verbose

# Dengan output directory custom
python test/test_runner.py --output-dir ./my_test_results
```

### 2. Menjalankan Kategori Test Tertentu

```bash
# Training tests saja
python test/test_runner.py --category training

# Fine-tuning tests saja
python test/test_runner.py --category fine-tuning

# Integration tests saja
python test/test_runner.py --category integration
```

### 3. Menjalankan Test Spesifik

```bash
# Test training tertentu
python test/test_runner.py --test test_basic_training

# Test fine-tuning tertentu
python test/test_runner.py --test test_basic_fine_tuning

# Test integration tertentu
python test/test_runner.py --test test_complete_training_pipeline
```

### 4. Menjalankan dengan Cleanup

```bash
# Menjalankan tests dan cleanup temporary files
python test/test_runner.py --cleanup
```

## 📊 Test Categories

### Training Tests (`test_training.py`)

Test untuk functionality training model:

- **Basic Training**: Training dasar dengan PPO
- **Multi-Algorithm Training**: Training dengan PPO, DQN, A2C
- **Validation Training**: Training dengan validation split
- **Progress Monitoring**: Monitoring progress training
- **Model Checkpointing**: Saving model selama training
- **Custom Reward Functions**: Training dengan reward function custom
- **Data Size Variations**: Training dengan berbagai ukuran data
- **Error Handling**: Handling error scenarios
- **Performance Metrics**: Collection metrics training

### Fine-tuning Tests (`test_fine_tuning.py`)

Test untuk functionality fine-tuning:

- **Basic Fine-tuning**: Fine-tuning dasar
- **Learning Rate Variations**: Fine-tuning dengan berbagai learning rate
- **Layer Freezing**: Fine-tuning dengan frozen layers
- **Limited Data Fine-tuning**: Fine-tuning dengan data terbatas
- **Performance Comparison**: Perbandingan base vs fine-tuned model
- **Hyperparameter Optimization**: Fine-tuning dengan hyperparameter optimization
- **Early Stopping**: Fine-tuning dengan early stopping
- **Custom Loss Functions**: Fine-tuning dengan loss function custom
- **Error Handling**: Handling error scenarios
- **Model Compatibility**: Fine-tuning dengan berbagai model types
- **Metadata Tracking**: Tracking metadata fine-tuning

### Integration Tests (`test_integration.py`)

Test untuk end-to-end workflow:

- **Complete Training Pipeline**: Pipeline training lengkap
- **Complete Fine-tuning Pipeline**: Pipeline fine-tuning lengkap
- **Model Lifecycle Management**: Management lifecycle model
- **Performance Monitoring Integration**: Integrasi monitoring performance
- **CLI Integration**: Testing CLI interface
- **Error Handling Integration**: Error handling dalam integration
- **Multi-Algorithm Integration**: Integration dengan berbagai algoritma
- **Data Preprocessing Integration**: Integration preprocessing data
- **End-to-End Workflow**: Workflow lengkap dari data ke deployment

## 📈 Test Reports

Test runner akan menghasilkan reports dalam format:

### JSON Report
```json
{
  "timestamp": "2024-01-01T12:00:00",
  "summary": {
    "training": {
      "total_tests": 9,
      "failures": 0,
      "errors": 0,
      "success_rate": 1.0
    },
    "fine_tuning": {
      "total_tests": 11,
      "failures": 0,
      "errors": 0,
      "success_rate": 1.0
    },
    "integration": {
      "total_tests": 9,
      "failures": 0,
      "errors": 0,
      "success_rate": 1.0
    },
    "overall": {
      "total_tests": 29,
      "failures": 0,
      "errors": 0,
      "success_rate": 1.0,
      "duration_seconds": 120.5
    }
  },
  "details": [...],
  "errors": []
}
```

### Text Report
```
XTrade-AI Test Report
==================================================

Generated: 2024-01-01T12:00:00
Duration: 120.50 seconds

SUMMARY
--------------------
TRAINING:
  Total tests: 9
  Failures: 0
  Errors: 0
  Success rate: 100.00%

FINE_TUNING:
  Total tests: 11
  Failures: 0
  Errors: 0
  Success rate: 100.00%

INTEGRATION:
  Total tests: 9
  Failures: 0
  Errors: 0
  Success rate: 100.00%

OVERALL:
  Total tests: 29
  Failures: 0
  Errors: 0
  Success rate: 100.00%
```

## 🔧 Configuration

### Test Data Generation

Tests menggunakan synthetic data yang di-generate secara otomatis:

- **OHLCV Data**: Price data dengan trend dan volatility
- **Technical Indicators**: RSI, MACD, Bollinger Bands, dll.
- **Multiple Timeframes**: Data untuk training, validation, fine-tuning, dan testing

### Test Environment

- **Temporary Directories**: Setiap test menggunakan temporary directory
- **Cleanup**: Automatic cleanup setelah test selesai
- **Isolation**: Tests diisolasi satu sama lain

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Pastikan berada di root directory
   cd /path/to/xtrade-ai
   python test/test_runner.py
   ```

2. **Missing Dependencies**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Memory Issues**
   ```bash
   # Jalankan dengan cleanup
   python test/test_runner.py --cleanup
   ```

4. **Timeout Issues**
   ```bash
   # Jalankan test tertentu saja
   python test/test_runner.py --test test_basic_training
   ```

### Debug Mode

```bash
# Enable verbose logging
python test/test_runner.py --verbose

# Check log files di test_results/
```

## 📝 Adding New Tests

### Menambah Test Training

1. Edit `test_training.py`
2. Tambah method test baru:
   ```python
   def test_new_training_feature(self):
       """Test new training feature."""
       # Test implementation
       pass
   ```
3. Update `test_runner.py` dengan test baru

### Menambah Test Fine-tuning

1. Edit `test_fine_tuning.py`
2. Tambah method test baru
3. Update `test_runner.py`

### Menambah Integration Test

1. Edit `test_integration.py`
2. Tambah method test baru
3. Update `test_runner.py`

## 🎯 Best Practices

### Writing Tests

1. **Isolation**: Setiap test harus independent
2. **Cleanup**: Selalu cleanup resources
3. **Assertions**: Gunakan assertions yang meaningful
4. **Documentation**: Dokumentasikan test purpose
5. **Error Handling**: Test error scenarios

### Running Tests

1. **Regular Runs**: Jalankan tests secara regular
2. **CI/CD**: Integrate dengan CI/CD pipeline
3. **Monitoring**: Monitor test results dan trends
4. **Performance**: Optimize test performance

## 📊 Performance Metrics

Test suite melaporkan:

- **Success Rate**: Percentage tests yang passed
- **Duration**: Total waktu eksekusi
- **Failures**: Number of test failures
- **Errors**: Number of test errors
- **Coverage**: Test coverage metrics

## 🔗 Integration dengan CI/CD

### GitHub Actions Example

```yaml
name: XTrade-AI Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.11
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python test/test_runner.py --cleanup
      - name: Upload test results
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: test_results/
```

## 📞 Support

Untuk issues atau questions:

1. Check log files di `test_results/`
2. Run dengan `--verbose` flag
3. Check documentation framework
4. Create issue di repository

## 📄 License

Test suite ini mengikuti license yang sama dengan framework XTrade-AI.

# Installation

## Requirements
- Python 3.8+
- pip
- (Optional) NVIDIA GPU for PyTorch CUDA builds

## Steps

### Option 1: Install with all dependencies (recommended for development)
```bash
cd clients/vendor/xtrade-ai
pip install -r requirements.txt
```

### Option 2: Install minimal dependencies (for production or if you encounter issues)
```bash
cd clients/vendor/xtrade-ai
pip install -r requirements-minimal.txt
```

### Option 3: Install with optional dependencies
```bash
cd clients/vendor/xtrade-ai
pip install -r requirements.txt
pip install -e .[ta,dev,viz,monitor,performance,database,api]
```

Optional: Install PyTorch with CUDA (adjust version as needed):
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Notes
- **TA-Lib**: Optional dependency that requires system installation. If you need TA-Lib:
  - **Ubuntu/Debian**: `sudo apt-get install ta-lib`
  - **macOS**: `brew install ta-lib`
  - **Windows**: Download from [TA-Lib website](http://ta-lib.org/hdr_dw.html)
  - Then install Python package: `pip install ta-lib>=0.4.24,<1.0.0`
- For sb3-contrib (TRPO, QRDQN) ensure `sb3-contrib>=2.4.0` is installed (included in requirements).
- If your environment is externally managed, create a virtualenv and use its pip.
- If you encounter installation issues, try the minimal requirements first: `pip install -r requirements-minimal.txt`

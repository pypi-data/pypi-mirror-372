# XTrade-AI Framework Cache Cleanup Script (PowerShell)
Write-Host "🧹 Cleaning XTrade-AI Framework cache and temporary files..." -ForegroundColor Green

# Clean Python cache
Write-Host "Cleaning Python cache..." -ForegroundColor Yellow
Get-ChildItem -Path . -Recurse -Directory -Name "__pycache__" | ForEach-Object { Remove-Item -Path $_ -Recurse -Force -ErrorAction SilentlyContinue }
Get-ChildItem -Path . -Recurse -File -Filter "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Recurse -File -Filter "*.pyo" | Remove-Item -Force -ErrorAction SilentlyContinue

# Clean build artifacts
Write-Host "Cleaning build artifacts..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Path "build" -Recurse -Force -ErrorAction SilentlyContinue }
if (Test-Path "dist") { Remove-Item -Path "dist" -Recurse -Force -ErrorAction SilentlyContinue }
Get-ChildItem -Path . -Directory -Filter "*.egg-info" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Clean test artifacts
Write-Host "Cleaning test artifacts..." -ForegroundColor Yellow
if (Test-Path ".pytest_cache") { Remove-Item -Path ".pytest_cache" -Recurse -Force -ErrorAction SilentlyContinue }
if (Test-Path "test_results") { Remove-Item -Path "test_results" -Recurse -Force -ErrorAction SilentlyContinue }
if (Test-Path "htmlcov") { Remove-Item -Path "htmlcov" -Recurse -Force -ErrorAction SilentlyContinue }
if (Test-Path ".coverage") { Remove-Item -Path ".coverage" -Force -ErrorAction SilentlyContinue }

# Clean Docker cache (if Docker is available)
try {
    $dockerVersion = docker --version 2>$null
    if ($dockerVersion) {
        Write-Host "Cleaning Docker cache..." -ForegroundColor Yellow
        docker system prune -f 2>$null
    }
} catch {
    Write-Host "Docker not available, skipping Docker cache cleanup" -ForegroundColor Gray
}

# Clean pip cache
Write-Host "Cleaning pip cache..." -ForegroundColor Yellow
try {
    pip cache purge 2>$null
} catch {
    Write-Host "Pip cache purge not available" -ForegroundColor Gray
}

# Clean git cache (if in git repository)
if (Test-Path ".git") {
    Write-Host "Cleaning git cache..." -ForegroundColor Yellow
    git gc --prune=now 2>$null
}

Write-Host "✅ Cache cleanup completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Current Python version:" -ForegroundColor Cyan
python --version
Write-Host ""
Write-Host "Current pip version:" -ForegroundColor Cyan
pip --version
Write-Host ""
Write-Host "Framework ready for deployment! 🚀" -ForegroundColor Green

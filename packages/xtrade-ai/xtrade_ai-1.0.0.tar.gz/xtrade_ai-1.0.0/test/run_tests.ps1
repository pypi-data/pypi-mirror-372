# XTrade-AI Test Runner Script (PowerShell)
# Script untuk menjalankan test suite dengan mudah di Windows

param(
    [string]$Category = "all",
    [string]$Test = "",
    [switch]$Verbose,
    [string]$OutputDir = "test_results",
    [switch]$Cleanup,
    [switch]$Quick,
    [switch]$Full,
    [switch]$CI,
    [switch]$Help
)

# Function to show help
function Show-Help {
    Write-Host "XTrade-AI Test Runner" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\run_tests.ps1 [OPTIONS]" -ForegroundColor White
    Write-Host ""
    Write-Host "Options:" -ForegroundColor White
    Write-Host "  -Help                    Show this help message" -ForegroundColor Yellow
    Write-Host "  -Category CAT            Run specific test category (training|fine-tuning|integration|all)" -ForegroundColor Yellow
    Write-Host "  -Test TEST               Run specific test method" -ForegroundColor Yellow
    Write-Host "  -Verbose                 Enable verbose output" -ForegroundColor Yellow
    Write-Host "  -OutputDir DIR           Set output directory for test results" -ForegroundColor Yellow
    Write-Host "  -Cleanup                 Clean up test artifacts after completion" -ForegroundColor Yellow
    Write-Host "  -Quick                   Run quick test suite (subset of tests)" -ForegroundColor Yellow
    Write-Host "  -Full                    Run full test suite (all tests)" -ForegroundColor Yellow
    Write-Host "  -CI                      Run in CI mode (minimal output, exit codes)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor White
    Write-Host "  .\run_tests.ps1                      # Run all tests" -ForegroundColor Gray
    Write-Host "  .\run_tests.ps1 -Category training  # Run training tests only" -ForegroundColor Gray
    Write-Host "  .\run_tests.ps1 -Test test_basic_training  # Run specific test" -ForegroundColor Gray
    Write-Host "  .\run_tests.ps1 -Quick              # Run quick test suite" -ForegroundColor Gray
    Write-Host "  .\run_tests.ps1 -CI                 # Run in CI mode" -ForegroundColor Gray
    Write-Host ""
}

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Show help if requested
if ($Help) {
    Show-Help
    exit 0
}

# Check if we're in the right directory
if (-not (Test-Path "xtrade_ai\__init__.py")) {
    Write-Error "Please run this script from the XTrade-AI root directory"
    exit 1
}

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Status "Found Python: $pythonVersion"
} catch {
    Write-Error "Python is not installed or not in PATH"
    exit 1
}

# Check if test files exist
if (-not (Test-Path "test\test_runner.py")) {
    Write-Error "Test runner not found. Please ensure test files are present."
    exit 1
}

# Create output directory
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

# Function to run tests
function Run-Tests {
    param([string]$Args)
    Write-Status "Running tests with arguments: $Args"
    
    # Run the test runner
    $result = python test\test_runner.py $Args.Split(" ")
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Tests completed successfully"
        return $true
    } else {
        Write-Error "Tests failed"
        return $false
    }
}

# Function to run quick tests
function Run-QuickTests {
    Write-Status "Running quick test suite..."
    
    # Run basic tests only
    $quickTests = @(
        "test_basic_training",
        "test_basic_fine_tuning",
        "test_complete_training_pipeline"
    )
    
    $failed = $false
    
    foreach ($test in $quickTests) {
        Write-Status "Running $test..."
        $args = "--test $test --output-dir $OutputDir"
        if ($Verbose) { $args += " --verbose" }
        if ($Cleanup) { $args += " --cleanup" }
        
        if (Run-Tests $args) {
            Write-Success "$test passed"
        } else {
            Write-Error "$test failed"
            $failed = $true
        }
    }
    
    return -not $failed
}

# Function to run CI tests
function Run-CITests {
    Write-Status "Running CI test suite..."
    
    # Run tests with minimal output
    $ciArgs = "--output-dir $OutputDir --cleanup"
    
    if (Run-Tests $ciArgs) {
        Write-Success "CI tests passed"
        return $true
    } else {
        Write-Error "CI tests failed"
        return $false
    }
}

# Main execution
function Main {
    Write-Status "Starting XTrade-AI Test Suite"
    Write-Status "Output directory: $OutputDir"
    
    # Check Python dependencies
    Write-Status "Checking Python dependencies..."
    try {
        python -c "import pandas, numpy, torch" 2>$null
        Write-Success "All dependencies found"
    } catch {
        Write-Warning "Some dependencies may be missing. Consider running: pip install -r requirements.txt"
    }
    
    # Determine what to run
    if ($CI) {
        $success = Run-CITests
    } elseif ($Quick) {
        $success = Run-QuickTests
    } elseif ($Test -ne "") {
        # Run specific test
        $args = "--test $Test --output-dir $OutputDir"
        if ($Verbose) { $args += " --verbose" }
        if ($Cleanup) { $args += " --cleanup" }
        $success = Run-Tests $args
    } else {
        # Run category or all tests
        $args = "--category $Category --output-dir $OutputDir"
        if ($Verbose) { $args += " --verbose" }
        if ($Cleanup) { $args += " --cleanup" }
        $success = Run-Tests $args
    }
    
    # Show results
    if ($success) {
        Write-Success "All tests completed successfully!"
        
        # Show test results summary if available
        if (Test-Path $OutputDir) {
            $reportFiles = Get-ChildItem -Path $OutputDir -Filter "test_report_*.txt" | Select-Object -First 1
            if ($reportFiles) {
                Write-Status "Test results summary:"
                Write-Host ""
                Get-Content $reportFiles.FullName
                Write-Host ""
            }
        }
    } else {
        Write-Error "Some tests failed. Check the output above for details."
        
        # Show error summary if available
        if (Test-Path $OutputDir) {
            $logFiles = Get-ChildItem -Path $OutputDir -Filter "*.log" | Select-Object -First 1
            if ($logFiles) {
                Write-Status "Recent errors from log:"
                Write-Host ""
                Get-Content $logFiles.FullName -Tail 20 | Where-Object { $_ -match "(ERROR|FAIL)" }
                Write-Host ""
            }
        }
    }
    
    return $success
}

# Run main function
$success = Main
if (-not $success) {
    exit 1
} else {
    exit 0
}

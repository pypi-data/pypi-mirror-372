#!/bin/bash

# XTrade-AI Test Runner Script
# Script untuk menjalankan test suite dengan mudah

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show help
show_help() {
    echo "XTrade-AI Test Runner"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help              Show this help message"
    echo "  -c, --category CAT      Run specific test category (training|fine-tuning|integration|all)"
    echo "  -t, --test TEST         Run specific test method"
    echo "  -v, --verbose           Enable verbose output"
    echo "  -o, --output-dir DIR    Set output directory for test results"
    echo "  --cleanup               Clean up test artifacts after completion"
    echo "  --quick                 Run quick test suite (subset of tests)"
    echo "  --full                  Run full test suite (all tests)"
    echo "  --ci                    Run in CI mode (minimal output, exit codes)"
    echo ""
    echo "Examples:"
    echo "  $0                      # Run all tests"
    echo "  $0 -c training          # Run training tests only"
    echo "  $0 -t test_basic_training  # Run specific test"
    echo "  $0 --quick              # Run quick test suite"
    echo "  $0 --ci                 # Run in CI mode"
    echo ""
}

# Default values
CATEGORY="all"
TEST_METHOD=""
VERBOSE=""
OUTPUT_DIR="test_results"
CLEANUP=""
QUICK_MODE=""
CI_MODE=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -c|--category)
            CATEGORY="$2"
            shift 2
            ;;
        -t|--test)
            TEST_METHOD="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE="--verbose"
            shift
            ;;
        -o|--output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --cleanup)
            CLEANUP="--cleanup"
            shift
            ;;
        --quick)
            QUICK_MODE="--quick"
            shift
            ;;
        --full)
            QUICK_MODE=""
            shift
            ;;
        --ci)
            CI_MODE="--ci"
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Check if we're in the right directory
if [[ ! -f "xtrade_ai/__init__.py" ]]; then
    print_error "Please run this script from the XTrade-AI root directory"
    exit 1
fi

# Check if Python is available
if ! command -v python &> /dev/null; then
    print_error "Python is not installed or not in PATH"
    exit 1
fi

# Check if test files exist
if [[ ! -f "test/test_runner.py" ]]; then
    print_error "Test runner not found. Please ensure test files are present."
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Function to run tests
run_tests() {
    local args="$1"
    print_status "Running tests with arguments: $args"
    
    # Run the test runner
    if python test/test_runner.py $args; then
        print_success "Tests completed successfully"
        return 0
    else
        print_error "Tests failed"
        return 1
    fi
}

# Function to run quick tests
run_quick_tests() {
    print_status "Running quick test suite..."
    
    # Run basic tests only
    local quick_tests=(
        "test_basic_training"
        "test_basic_fine_tuning"
        "test_complete_training_pipeline"
    )
    
    local failed=0
    
    for test in "${quick_tests[@]}"; do
        print_status "Running $test..."
        if python test/test_runner.py --test "$test" --output-dir "$OUTPUT_DIR" $VERBOSE $CLEANUP; then
            print_success "$test passed"
        else
            print_error "$test failed"
            failed=1
        fi
    done
    
    return $failed
}

# Function to run CI tests
run_ci_tests() {
    print_status "Running CI test suite..."
    
    # Run tests with minimal output
    local ci_args="--output-dir $OUTPUT_DIR --cleanup"
    
    if run_tests "$ci_args"; then
        print_success "CI tests passed"
        return 0
    else
        print_error "CI tests failed"
        return 1
    fi
}

# Main execution
main() {
    print_status "Starting XTrade-AI Test Suite"
    print_status "Output directory: $OUTPUT_DIR"
    
    # Check Python dependencies
    print_status "Checking Python dependencies..."
    if ! python -c "import pandas, numpy, torch" 2>/dev/null; then
        print_warning "Some dependencies may be missing. Consider running: pip install -r requirements.txt"
    fi
    
    # Determine what to run
    if [[ -n "$CI_MODE" ]]; then
        run_ci_tests
    elif [[ -n "$QUICK_MODE" ]]; then
        run_quick_tests
    elif [[ -n "$TEST_METHOD" ]]; then
        # Run specific test
        local args="--test $TEST_METHOD --output-dir $OUTPUT_DIR $VERBOSE $CLEANUP"
        run_tests "$args"
    else
        # Run category or all tests
        local args="--category $CATEGORY --output-dir $OUTPUT_DIR $VERBOSE $CLEANUP"
        run_tests "$args"
    fi
    
    local exit_code=$?
    
    # Show results
    if [[ $exit_code -eq 0 ]]; then
        print_success "All tests completed successfully!"
        
        # Show test results summary if available
        if [[ -d "$OUTPUT_DIR" ]]; then
            local report_files=($(find "$OUTPUT_DIR" -name "test_report_*.txt" -type f | head -1))
            if [[ ${#report_files[@]} -gt 0 ]]; then
                print_status "Test results summary:"
                echo ""
                cat "${report_files[0]}"
                echo ""
            fi
        fi
    else
        print_error "Some tests failed. Check the output above for details."
        
        # Show error summary if available
        if [[ -d "$OUTPUT_DIR" ]]; then
            local log_files=($(find "$OUTPUT_DIR" -name "*.log" -type f | head -1))
            if [[ ${#log_files[@]} -gt 0 ]]; then
                print_status "Recent errors from log:"
                echo ""
                tail -20 "${log_files[0]}" | grep -E "(ERROR|FAIL)" || true
                echo ""
            fi
        fi
    fi
    
    return $exit_code
}

# Run main function
main

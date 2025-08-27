#!/usr/bin/env python3
"""
Test runner for XTrade-AI training and fine-tuning tests.

This script provides a comprehensive test runner that can:
- Run individual test modules
- Run all tests with different configurations
- Generate test reports
- Handle test failures gracefully
- Provide detailed logging and progress tracking
"""

import argparse
import json
import logging
import os
import shutil
import sys
import tempfile
import time
import unittest
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from test_fine_tuning import TestFineTuning
from test_integration import TestIntegration

# Import test modules
from test_training import TestTraining


class TestRunner:
    """Comprehensive test runner for XTrade-AI tests."""

    def __init__(self, verbose=False, output_dir=None):
        """
        Initialize test runner.

        Args:
            verbose: Enable verbose output
            output_dir: Directory for test outputs
        """
        self.verbose = verbose
        self.output_dir = Path(output_dir) if output_dir else Path("test_results")
        self.output_dir.mkdir(exist_ok=True)

        # Set up logging
        self._setup_logging()

        # Test results storage
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "summary": {},
            "details": [],
            "errors": [],
            "warnings": [],
        }

    def _setup_logging(self):
        """Set up logging configuration."""
        log_level = logging.DEBUG if self.verbose else logging.INFO

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Set up file handler
        log_file = (
            self.output_dir / f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)

        # Set up console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)

        # Configure root logger
        logging.basicConfig(level=log_level, handlers=[file_handler, console_handler])

        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Test runner initialized. Log file: {log_file}")

    def run_single_test(self, test_class, test_method=None):
        """
        Run a single test class or method.

        Args:
            test_class: Test class to run
            test_method: Specific test method to run (optional)

        Returns:
            Test result
        """
        self.logger.info(f"Running test: {test_class.__name__}")

        # Create test suite
        if test_method:
            suite = unittest.TestSuite()
            suite.addTest(test_class(test_method))
        else:
            suite = unittest.TestLoader().loadTestsFromTestCase(test_class)

        # Run test
        runner = unittest.TextTestRunner(verbosity=2 if self.verbose else 1)
        result = runner.run(suite)

        # Store results
        test_result = {
            "test_class": test_class.__name__,
            "test_method": test_method,
            "tests_run": result.testsRun,
            "failures": len(result.failures),
            "errors": len(result.errors),
            "skipped": len(result.skipped) if hasattr(result, "skipped") else 0,
            "success": result.wasSuccessful(),
        }

        self.test_results["details"].append(test_result)

        # Log results
        if result.wasSuccessful():
            self.logger.info(
                f"[PASS] {test_class.__name__} passed: {result.testsRun} tests"
            )
        else:
            self.logger.error(
                f"✗ {test_class.__name__} failed: {len(result.failures)} failures, {len(result.errors)} errors"
            )

            # Store error details
            for failure in result.failures:
                self.test_results["errors"].append(
                    {
                        "type": "failure",
                        "test": str(failure[0]),
                        "message": str(failure[1]),
                    }
                )

            for error in result.errors:
                self.test_results["errors"].append(
                    {"type": "error", "test": str(error[0]), "message": str(error[1])}
                )

        return result

    def run_training_tests(self):
        """Run all training tests."""
        self.logger.info("=" * 60)
        self.logger.info("RUNNING TRAINING TESTS")
        self.logger.info("=" * 60)

        training_tests = [
            "test_basic_training",
            "test_training_with_different_algorithms",
            "test_training_with_validation",
            "test_training_progress_monitoring",
            "test_model_saving_during_training",
            "test_training_with_custom_reward_function",
            "test_training_with_different_data_sizes",
            "test_training_error_handling",
            "test_training_performance_metrics",
        ]

        results = []
        for test_method in training_tests:
            try:
                result = self.run_single_test(TestTraining, test_method)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error running {test_method}: {e}")
                self.test_results["errors"].append(
                    {"type": "exception", "test": test_method, "message": str(e)}
                )

        # Update summary
        total_tests = sum(r.testsRun for r in results)
        total_failures = sum(len(r.failures) for r in results)
        total_errors = sum(len(r.errors) for r in results)

        self.test_results["summary"]["training"] = {
            "total_tests": total_tests,
            "failures": total_failures,
            "errors": total_errors,
            "success_rate": (
                (total_tests - total_failures - total_errors) / total_tests
                if total_tests > 0
                else 0
            ),
        }

        return results

    def run_fine_tuning_tests(self):
        """Run all fine-tuning tests."""
        self.logger.info("=" * 60)
        self.logger.info("RUNNING FINE-TUNING TESTS")
        self.logger.info("=" * 60)

        fine_tuning_tests = [
            "test_basic_fine_tuning",
            "test_fine_tuning_with_different_learning_rates",
            "test_fine_tuning_with_layer_freezing",
            "test_fine_tuning_with_limited_data",
            "test_fine_tuning_performance_comparison",
            "test_fine_tuning_with_hyperparameter_optimization",
            "test_fine_tuning_with_early_stopping",
            "test_fine_tuning_with_custom_loss_function",
            "test_fine_tuning_error_handling",
            "test_fine_tuning_model_compatibility",
            "test_fine_tuning_metadata_tracking",
        ]

        results = []
        for test_method in fine_tuning_tests:
            try:
                result = self.run_single_test(TestFineTuning, test_method)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error running {test_method}: {e}")
                self.test_results["errors"].append(
                    {"type": "exception", "test": test_method, "message": str(e)}
                )

        # Update summary
        total_tests = sum(r.testsRun for r in results)
        total_failures = sum(len(r.failures) for r in results)
        total_errors = sum(len(r.errors) for r in results)

        self.test_results["summary"]["fine_tuning"] = {
            "total_tests": total_tests,
            "failures": total_failures,
            "errors": total_errors,
            "success_rate": (
                (total_tests - total_failures - total_errors) / total_tests
                if total_tests > 0
                else 0
            ),
        }

        return results

    def run_integration_tests(self):
        """Run all integration tests."""
        self.logger.info("=" * 60)
        self.logger.info("RUNNING INTEGRATION TESTS")
        self.logger.info("=" * 60)

        integration_tests = [
            "test_complete_training_pipeline",
            "test_complete_fine_tuning_pipeline",
            "test_model_lifecycle_management",
            "test_performance_monitoring_integration",
            "test_cli_integration",
            "test_error_handling_integration",
            "test_multi_algorithm_integration",
            "test_data_preprocessing_integration",
            "test_end_to_end_workflow",
        ]

        results = []
        for test_method in integration_tests:
            try:
                result = self.run_single_test(TestIntegration, test_method)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error running {test_method}: {e}")
                self.test_results["errors"].append(
                    {"type": "exception", "test": test_method, "message": str(e)}
                )

        # Update summary
        total_tests = sum(r.testsRun for r in results)
        total_failures = sum(len(r.failures) for r in results)
        total_errors = sum(len(r.errors) for r in results)

        self.test_results["summary"]["integration"] = {
            "total_tests": total_tests,
            "failures": total_failures,
            "errors": total_errors,
            "success_rate": (
                (total_tests - total_failures - total_errors) / total_tests
                if total_tests > 0
                else 0
            ),
        }

        return results

    def run_all_tests(self):
        """Run all tests."""
        self.logger.info("=" * 60)
        self.logger.info("STARTING COMPREHENSIVE TEST SUITE")
        self.logger.info("=" * 60)

        start_time = time.time()

        # Run all test categories
        training_results = self.run_training_tests()
        fine_tuning_results = self.run_fine_tuning_tests()
        integration_results = self.run_integration_tests()

        end_time = time.time()
        duration = end_time - start_time

        # Calculate overall summary
        all_results = training_results + fine_tuning_results + integration_results
        total_tests = sum(r.testsRun for r in all_results)
        total_failures = sum(len(r.failures) for r in all_results)
        total_errors = sum(len(r.errors) for r in all_results)

        self.test_results["summary"]["overall"] = {
            "total_tests": total_tests,
            "failures": total_failures,
            "errors": total_errors,
            "success_rate": (
                (total_tests - total_failures - total_errors) / total_tests
                if total_tests > 0
                else 0
            ),
            "duration_seconds": duration,
        }

        # Generate final report
        self._generate_report()

        self.logger.info("=" * 60)
        self.logger.info("TEST SUITE COMPLETED")
        self.logger.info(f"Total tests: {total_tests}")
        self.logger.info(f"Failures: {total_failures}")
        self.logger.info(f"Errors: {total_errors}")
        self.logger.info(
            f"Success rate: {self.test_results['summary']['overall']['success_rate']:.2%}"
        )
        self.logger.info(f"Duration: {duration:.2f} seconds")
        self.logger.info("=" * 60)

        return all_results

    def _generate_report(self):
        """Generate comprehensive test report."""
        report_file = (
            self.output_dir
            / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        with open(report_file, "w") as f:
            json.dump(self.test_results, f, indent=2)

        # Generate human-readable report
        text_report_file = (
            self.output_dir
            / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )

        with open(text_report_file, "w") as f:
            f.write("XTrade-AI Test Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated: {self.test_results['timestamp']}\n")
            f.write(
                f"Duration: {self.test_results['summary']['overall']['duration_seconds']:.2f} seconds\n\n"
            )

            f.write("SUMMARY\n")
            f.write("-" * 20 + "\n")
            for category, stats in self.test_results["summary"].items():
                if category != "overall":
                    f.write(f"{category.upper()}:\n")
                    f.write(f"  Total tests: {stats['total_tests']}\n")
                    f.write(f"  Failures: {stats['failures']}\n")
                    f.write(f"  Errors: {stats['errors']}\n")
                    f.write(f"  Success rate: {stats['success_rate']:.2%}\n\n")

            f.write("OVERALL:\n")
            overall = self.test_results["summary"]["overall"]
            f.write(f"  Total tests: {overall['total_tests']}\n")
            f.write(f"  Failures: {overall['failures']}\n")
            f.write(f"  Errors: {overall['errors']}\n")
            f.write(f"  Success rate: {overall['success_rate']:.2%}\n\n")

            if self.test_results["errors"]:
                f.write("ERRORS AND FAILURES\n")
                f.write("-" * 20 + "\n")
                for error in self.test_results["errors"]:
                    f.write(f"Type: {error['type']}\n")
                    f.write(f"Test: {error['test']}\n")
                    f.write(f"Message: {error['message']}\n")
                    f.write("-" * 10 + "\n")

        self.logger.info(f"Test report saved to: {report_file}")
        self.logger.info(f"Text report saved to: {text_report_file}")

    def cleanup(self):
        """Clean up test artifacts."""
        # Clean up temporary directories
        temp_dirs = [d for d in Path("/tmp").glob("tmp*") if d.is_dir()]
        for temp_dir in temp_dirs:
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                self.logger.warning(f"Could not clean up {temp_dir}: {e}")


def main():
    """Main function for test runner."""
    parser = argparse.ArgumentParser(description="XTrade-AI Test Runner")
    parser.add_argument(
        "--category",
        choices=["training", "fine-tuning", "integration", "all"],
        default="all",
        help="Test category to run",
    )
    parser.add_argument("--test", help="Specific test method to run")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "--output-dir", default="test_results", help="Directory for test outputs"
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Clean up test artifacts after completion",
    )

    args = parser.parse_args()

    # Initialize test runner
    runner = TestRunner(verbose=args.verbose, output_dir=args.output_dir)

    try:
        if args.test:
            # Run specific test
            if "training" in args.test.lower():
                runner.run_single_test(TestTraining, args.test)
            elif "fine" in args.test.lower() or "tuning" in args.test.lower():
                runner.run_single_test(TestFineTuning, args.test)
            elif "integration" in args.test.lower():
                runner.run_single_test(TestIntegration, args.test)
            else:
                print(f"Unknown test: {args.test}")
                sys.exit(1)
        elif args.category == "training":
            runner.run_training_tests()
        elif args.category == "fine-tuning":
            runner.run_fine_tuning_tests()
        elif args.category == "integration":
            runner.run_integration_tests()
        else:  # all
            runner.run_all_tests()

    except KeyboardInterrupt:
        runner.logger.info("Test run interrupted by user")
        sys.exit(1)
    except Exception as e:
        runner.logger.error(f"Test run failed: {e}")
        sys.exit(1)
    finally:
        if args.cleanup:
            runner.cleanup()

    # Exit with appropriate code
    overall_success = (
        runner.test_results["summary"].get("overall", {}).get("success_rate", 0)
    )
    if overall_success < 0.8:  # Less than 80% success rate
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

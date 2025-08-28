#!/usr/bin/env python3
"""
Parallel Test Runner for XTrade-AI

This script runs tests in parallel to speed up the testing process.
It supports:
- Parallel execution of test categories
- Resource management
- Progress tracking
- Result aggregation
"""

import argparse
import concurrent.futures
import json
import logging
import os
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from test_runner import TestRunner


class ParallelTestRunner:
    """Parallel test runner for XTrade-AI tests."""

    def __init__(self, max_workers: int = 4, output_dir: str = "test_results_parallel"):
        """
        Initialize parallel test runner.

        Args:
            max_workers: Maximum number of parallel workers
            output_dir: Output directory for test results
        """
        self.max_workers = max_workers
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Set up logging
        self._setup_logging()

        # Test results storage
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "parallel_config": {
                "max_workers": max_workers,
                "output_dir": str(output_dir),
            },
            "categories": {},
            "summary": {},
            "errors": [],
        }

        # Thread lock for logging
        self.log_lock = threading.Lock()

    def _setup_logging(self):
        """Set up logging configuration."""
        log_file = (
            self.output_dir
            / f"parallel_test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )

        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Parallel test runner initialized. Log file: {log_file}")

    def run_category(self, category: str) -> Tuple[str, Dict[str, Any]]:
        """
        Run a single test category.

        Args:
            category: Test category to run

        Returns:
            Tuple of (category_name, results)
        """
        with self.log_lock:
            self.logger.info(f"Starting {category} tests...")

        try:
            # Create category-specific output directory
            category_output_dir = self.output_dir / category
            category_output_dir.mkdir(exist_ok=True)

            # Run the test category
            start_time = time.time()

            # Use subprocess to run test runner
            cmd = [
                sys.executable,
                "test/test_runner.py",
                "--category",
                category,
                "--output-dir",
                str(category_output_dir),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout per category
            )

            end_time = time.time()
            duration = end_time - start_time

            # Parse results
            if result.returncode == 0:
                status = "success"
                with self.log_lock:
                    self.logger.info(
                        f"[PASS] {category} tests completed successfully in {duration:.2f}s"
                    )
            else:
                status = "failed"
                with self.log_lock:
                    self.logger.error(f"✗ {category} tests failed in {duration:.2f}s")
                    self.logger.error(f"Error output: {result.stderr}")

            # Try to load test results if available
            test_results = {}
            report_files = list(category_output_dir.glob("test_report_*.json"))
            if report_files:
                try:
                    with open(report_files[0], "r") as f:
                        test_results = json.load(f)
                except Exception as e:
                    with self.log_lock:
                        self.logger.warning(
                            f"Could not load test results for {category}: {e}"
                        )

            category_result = {
                "status": status,
                "duration": duration,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "test_results": test_results,
            }

            return category, category_result

        except subprocess.TimeoutExpired:
            with self.log_lock:
                self.logger.error(f"✗ {category} tests timed out")

            return category, {
                "status": "timeout",
                "duration": 600,
                "return_code": -1,
                "stdout": "",
                "stderr": "Test execution timed out",
                "test_results": {},
            }

        except Exception as e:
            with self.log_lock:
                self.logger.error(f"✗ {category} tests failed with exception: {e}")

            return category, {
                "status": "exception",
                "duration": 0,
                "return_code": -1,
                "stdout": "",
                "stderr": str(e),
                "test_results": {},
            }

    def run_all_categories(self) -> Dict[str, Any]:
        """
        Run all test categories in parallel.

        Returns:
            Aggregated test results
        """
        self.logger.info(
            f"Starting parallel test execution with {self.max_workers} workers"
        )

        categories = ["training", "fine-tuning", "integration"]

        start_time = time.time()

        # Run categories in parallel
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as executor:
            # Submit all tasks
            future_to_category = {
                executor.submit(self.run_category, category): category
                for category in categories
            }

            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_category):
                category, result = future.result()
                self.results["categories"][category] = result

        end_time = time.time()
        total_duration = end_time - start_time

        # Calculate summary
        self._calculate_summary(total_duration)

        # Generate reports
        self._generate_reports()

        self.logger.info(f"Parallel test execution completed in {total_duration:.2f}s")

        return self.results

    def _calculate_summary(self, total_duration: float):
        """Calculate summary statistics."""
        total_tests = 0
        total_failures = 0
        total_errors = 0
        successful_categories = 0

        for category, result in self.results["categories"].items():
            if result["status"] == "success":
                successful_categories += 1

                # Extract test statistics from test results
                if "test_results" in result and "summary" in result["test_results"]:
                    category_summary = result["test_results"]["summary"].get(
                        category, {}
                    )
                    total_tests += category_summary.get("total_tests", 0)
                    total_failures += category_summary.get("failures", 0)
                    total_errors += category_summary.get("errors", 0)

        self.results["summary"] = {
            "total_duration": total_duration,
            "total_categories": len(self.results["categories"]),
            "successful_categories": successful_categories,
            "failed_categories": len(self.results["categories"])
            - successful_categories,
            "total_tests": total_tests,
            "total_failures": total_failures,
            "total_errors": total_errors,
            "success_rate": (
                successful_categories / len(self.results["categories"])
                if self.results["categories"]
                else 0
            ),
            "test_success_rate": (
                (total_tests - total_failures - total_errors) / total_tests
                if total_tests > 0
                else 0
            ),
        }

    def _generate_reports(self):
        """Generate comprehensive reports."""
        # JSON report
        report_file = (
            self.output_dir
            / f"parallel_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2)

        # Text report
        text_report_file = (
            self.output_dir
            / f"parallel_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        with open(text_report_file, "w") as f:
            f.write("XTrade-AI Parallel Test Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated: {self.results['timestamp']}\n")
            f.write(
                f"Total Duration: {self.results['summary']['total_duration']:.2f} seconds\n"
            )
            f.write(
                f"Max Workers: {self.results['parallel_config']['max_workers']}\n\n"
            )

            f.write("CATEGORY RESULTS\n")
            f.write("-" * 20 + "\n")
            for category, result in self.results["categories"].items():
                f.write(f"{category.upper()}:\n")
                f.write(f"  Status: {result['status']}\n")
                f.write(f"  Duration: {result['duration']:.2f}s\n")
                f.write(f"  Return Code: {result['return_code']}\n")
                if result["stderr"]:
                    f.write(f"  Error: {result['stderr'][:200]}...\n")
                f.write("\n")

            f.write("SUMMARY\n")
            f.write("-" * 20 + "\n")
            summary = self.results["summary"]
            f.write(f"Total Categories: {summary['total_categories']}\n")
            f.write(f"Successful Categories: {summary['successful_categories']}\n")
            f.write(f"Failed Categories: {summary['failed_categories']}\n")
            f.write(f"Category Success Rate: {summary['success_rate']:.2%}\n")
            f.write(f"Total Tests: {summary['total_tests']}\n")
            f.write(f"Total Failures: {summary['total_failures']}\n")
            f.write(f"Total Errors: {summary['total_errors']}\n")
            f.write(f"Test Success Rate: {summary['test_success_rate']:.2%}\n")

        self.logger.info(f"Parallel test report saved to: {report_file}")
        self.logger.info(f"Text report saved to: {text_report_file}")


def main():
    """Main function for parallel test runner."""
    parser = argparse.ArgumentParser(description="XTrade-AI Parallel Test Runner")
    parser.add_argument(
        "--max-workers", type=int, default=4, help="Maximum number of parallel workers"
    )
    parser.add_argument(
        "--output-dir",
        default="test_results_parallel",
        help="Output directory for test results",
    )
    parser.add_argument(
        "--categories",
        nargs="+",
        choices=["training", "fine-tuning", "integration"],
        default=["training", "fine-tuning", "integration"],
        help="Test categories to run",
    )
    parser.add_argument(
        "--timeout", type=int, default=600, help="Timeout per category in seconds"
    )

    args = parser.parse_args()

    # Check if we're in the right directory
    if not Path("xtrade_ai/__init__.py").exists():
        print("ERROR: Please run this script from the XTrade-AI root directory")
        sys.exit(1)

    # Check if test runner exists
    if not Path("test/test_runner.py").exists():
        print("ERROR: Test runner not found. Please ensure test files are present.")
        sys.exit(1)

    # Initialize parallel test runner
    runner = ParallelTestRunner(
        max_workers=args.max_workers, output_dir=args.output_dir
    )

    try:
        # Run tests
        results = runner.run_all_categories()

        # Print summary
        summary = results["summary"]
        print("\n" + "=" * 60)
        print("PARALLEL TEST EXECUTION COMPLETED")
        print("=" * 60)
        print(f"Total Duration: {summary['total_duration']:.2f} seconds")
        print(
            f"Categories: {summary['successful_categories']}/{summary['total_categories']} successful"
        )
        print(f"Category Success Rate: {summary['success_rate']:.2%}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Test Success Rate: {summary['test_success_rate']:.2%}")
        print("=" * 60)

        # Exit with appropriate code
        if summary["success_rate"] < 0.8:  # Less than 80% success rate
            sys.exit(1)
        else:
            sys.exit(0)

    except KeyboardInterrupt:
        print("\nTest execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Test execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import re
import threading
import time
import unittest
from io import StringIO
from unittest.mock import MagicMock, patch

from tuxparse.boot_test_parser import BootTestParser
from tuxparse.lib.base_log_parser import BaseLogParser


class TestMemoryLimits(unittest.TestCase):
    """Test suite for memory limits functionality in base_log_parser."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = BaseLogParser()
        self.boot_parser = BootTestParser()

    def test_memory_limits_basic_functionality(self):
        """Test basic memory limits functionality."""
        # Create a large number of test lines that would exceed the limit
        test_lines = []
        for i in range(50):  # More than the 30 limit
            test_lines.append(f"Test line {i} with unique content")

        # Create tests - should be limited to 30 lines processed
        tests_without_shas, tests_with_shas = self.parser.create_tests(
            "test-suite", "test-pattern", test_lines, None
        )

        # Should have one test (since no name extraction) but limited to 30 lines
        self.assertEqual(len(tests_without_shas), 1)

        # Verify the test contains only the first 30 lines
        test_name = "test-pattern"
        self.assertIn(test_name, tests_without_shas)
        actual_lines = tests_without_shas[test_name]
        self.assertEqual(len(actual_lines), 30)

        # Should contain the first 30 lines
        expected_lines = set(f"Test line {i} with unique content" for i in range(30))
        self.assertEqual(set(actual_lines), expected_lines)

    def test_memory_limits_with_logging(self):
        """Test that memory limits trigger appropriate logging."""
        # Create test lines that exceed the limit
        test_lines = [f"Repetitive pattern {i}" for i in range(50)]

        # Mock the logger to capture warning
        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            # Create tests - should trigger warning
            self.parser.create_tests("test-suite", "test-pattern", test_lines, None)

            # Should have logged a warning about truncation
            mock_logger.warning.assert_called_once()
            warning_msg = mock_logger.warning.call_args[0][0]
            self.assertIn("Truncated test creation", warning_msg)
            self.assertIn("30 tests", warning_msg)
            self.assertIn("test-pattern", warning_msg)
            self.assertIn("memory exhaustion", warning_msg)

    def test_memory_limits_with_different_patterns(self):
        """Test memory limits work with different test patterns."""
        # Test with different test names
        test_cases = [
            ("oops-pattern", [f"Oops pattern {i}" for i in range(40)]),
            ("panic-pattern", [f"Panic pattern {i}" for i in range(25)]),
            ("warning-pattern", [f"Warning pattern {i}" for i in range(50)]),
        ]

        for test_name, test_lines in test_cases:
            with patch("logging.getLogger") as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger

                tests_without_shas, _ = self.parser.create_tests(
                    "test-suite", test_name, test_lines, None
                )

                # Should respect the limit
                self.assertLessEqual(len(tests_without_shas), 30)

                # Should log warning if limit exceeded
                if len(test_lines) > 30:
                    mock_logger.warning.assert_called_once()
                    warning_msg = mock_logger.warning.call_args[0][0]
                    self.assertIn(test_name, warning_msg)
                else:
                    mock_logger.warning.assert_not_called()

    def test_memory_limits_with_name_extraction(self):
        """Test memory limits work with name extraction regex."""
        # Create test lines with extractable names that repeat patterns
        # to trigger the per-pattern memory limit
        test_lines = []
        # Create 35 lines for function_a and 35 lines for function_b
        for i in range(35):
            test_lines.append(f"Error in function_a: error message {i}")
            test_lines.append(f"Error in function_b: error message {i}")

        # Create regex to extract function names
        name_regex = re.compile(r"Error in (\w+):")

        # Create tests with name extraction
        tests_without_shas, _ = self.parser.create_tests(
            "test-suite", "error-pattern", test_lines, name_regex
        )

        # Should be limited to 30 tests per extracted pattern (function_a and function_b)
        # So we should have exactly 2 test patterns with 30 lines each = 60 total tests
        self.assertEqual(len(tests_without_shas), 2)

        # Each pattern should have exactly 30 lines (due to memory limit)
        for test_name, lines in tests_without_shas.items():
            self.assertEqual(len(lines), 30)

        # Should have extracted names for function_a and function_b
        expected_names = {"error-pattern-function_a", "error-pattern-function_b"}
        actual_names = set(tests_without_shas.keys())
        self.assertEqual(actual_names, expected_names)

    def test_memory_limits_with_shas(self):
        """Test memory limits work with SHA creation enabled."""
        # Create test lines that would exceed limits
        test_lines = [f"Unique test line {i}" for i in range(40)]

        # Create tests with SHA creation enabled
        tests_without_shas, tests_with_shas = self.parser.create_tests(
            "test-suite", "test-pattern", test_lines, None, create_shas=True
        )

        # Should be limited to 30 lines processed, resulting in 1 test
        self.assertEqual(len(tests_without_shas), 1)
        self.assertEqual(len(tests_without_shas["test-pattern"]), 30)

        # Should have SHA versions - one SHA test with all the lines
        self.assertEqual(len(tests_with_shas), 1)  # One SHA test

        # Verify SHA tests have appropriate names
        for test_name in tests_with_shas.keys():
            self.assertRegex(test_name, r"test-pattern-[a-f0-9]+$")
            # Should contain all 30 lines
            self.assertEqual(len(tests_with_shas[test_name]), 30)

    def test_memory_limits_integration_with_boot_parser(self):
        """Test memory limits integration with boot_test_parser."""
        # Create a log with repetitive patterns that would exceed limits
        log_excerpt = []
        for i in range(50):
            log_excerpt.append(
                f"[{i:8.3f}] Kernel panic - not syncing: repetitive panic {i}"
            )

        repetitive_log = "\n".join(log_excerpt)

        # Process with boot parser
        with patch("logging.Logger.warning") as mock_warning:
            results = self.boot_parser._process_log_section(
                repetitive_log, "boot", False
            )

            # Should have created limited number of tests
            boot_suite = results["log-parser-boot"]
            total_tests = len(boot_suite)

            # Should be reasonable number (not 50)
            self.assertLessEqual(total_tests, 30)

            # Should have logged warnings about truncation
            mock_warning.assert_called()

    def test_memory_limits_with_duplicate_lines(self):
        """Test memory limits with duplicate lines (should be deduplicated)."""
        # Create test lines with duplicates
        test_lines = []
        for i in range(20):
            test_lines.extend(
                [f"Duplicate line {i}", f"Duplicate line {i}"]
            )  # Each line twice

        # Add more unique lines to exceed limit
        for i in range(20):
            test_lines.append(f"Unique line {i}")

        # Should have 20 duplicate pairs + 20 unique = 40 unique lines, but limited to 30
        tests_without_shas, _ = self.parser.create_tests(
            "test-suite", "test-pattern", test_lines, None
        )

        # Should be limited to 30 lines processed (not 30 unique tests)
        self.assertEqual(len(tests_without_shas), 1)
        # The test should contain up to 30 unique lines (since duplicates are added to set)
        test_lines_count = len(tests_without_shas["test-pattern"])
        self.assertLessEqual(test_lines_count, 30)

    def test_memory_limits_boundary_conditions(self):
        """Test memory limits at boundary conditions."""
        # Test exactly at the limit
        test_lines_30 = [f"Line {i}" for i in range(30)]
        tests_without_shas, _ = self.parser.create_tests(
            "test-suite", "test-pattern", test_lines_30, None
        )
        self.assertEqual(len(tests_without_shas), 1)
        self.assertEqual(len(tests_without_shas["test-pattern"]), 30)

        # Test just under the limit
        test_lines_29 = [f"Line {i}" for i in range(29)]
        tests_without_shas, _ = self.parser.create_tests(
            "test-suite", "test-pattern", test_lines_29, None
        )
        self.assertEqual(len(tests_without_shas), 1)
        self.assertEqual(len(tests_without_shas["test-pattern"]), 29)

        # Test just over the limit
        test_lines_31 = [f"Line {i}" for i in range(31)]
        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            tests_without_shas, _ = self.parser.create_tests(
                "test-suite", "test-pattern", test_lines_31, None
            )

            self.assertEqual(len(tests_without_shas), 1)
            self.assertEqual(len(tests_without_shas["test-pattern"]), 30)
            mock_logger.warning.assert_called_once()

    def test_memory_limits_with_complex_patterns(self):
        """Test memory limits with complex regex patterns."""
        # Create test lines that match complex patterns
        test_lines = []
        for i in range(40):
            test_lines.extend(
                [
                    f"[{i:8.3f}] ------------[ cut here ]------------",
                    f"[{i:8.3f}] WARNING: CPU: 0 PID: {i} at kernel/test.c:123",
                    f"[{i:8.3f}] Modules linked in:",
                    f"[{i:8.3f}] ---[ end trace ]---",
                ]
            )

        complex_log = "\n".join(test_lines)

        # Process with boot parser (which has complex multi-line patterns)
        with patch("logging.Logger.warning") as mock_warning:
            results = self.boot_parser._process_log_section(complex_log, "boot", False)

            # Should have processed but with limits
            boot_suite = results["log-parser-boot"]
            self.assertGreater(len(boot_suite), 0)

            # Should not have excessive number of tests
            # Verify warning was called for memory limits
            self.assertTrue(mock_warning.called or len(boot_suite) < 35)
            total_tests = len(boot_suite)
            self.assertLessEqual(total_tests, 60)  # Reasonable upper bound

    def test_memory_limits_with_empty_input(self):
        """Test memory limits with empty input."""
        # Test with empty list
        tests_without_shas, tests_with_shas = self.parser.create_tests(
            "test-suite", "test-pattern", [], None
        )

        self.assertEqual(len(tests_without_shas), 0)
        self.assertEqual(len(tests_with_shas), 0)  # Empty defaultdict, not None

        # Test with list containing empty strings
        empty_lines = ["", "", ""]
        tests_without_shas, _ = self.parser.create_tests(
            "test-suite", "test-pattern", empty_lines, None
        )

        # Should create a single test with the empty content
        self.assertEqual(len(tests_without_shas), 1)

    def test_memory_limits_performance_impact(self):
        """Test that memory limits don't significantly impact performance."""

        # Create a reasonable number of test lines
        test_lines = [f"Performance test line {i}" for i in range(30)]

        # Time the operation
        start_time = time.time()
        tests_without_shas, _ = self.parser.create_tests(
            "test-suite", "test-pattern", test_lines, None
        )
        end_time = time.time()

        # Should complete quickly (less than 1 second for 30 tests)
        processing_time = end_time - start_time
        self.assertLess(processing_time, 1.0)

        # Should create one test with all lines (within limit)
        self.assertEqual(len(tests_without_shas), 1)
        self.assertEqual(len(tests_without_shas["test-pattern"]), 30)

    def test_memory_limits_thread_safety(self):
        """Test memory limits work correctly in multi-threaded scenarios."""

        results = {}

        def create_tests_worker(thread_id):
            """Worker function for threading test."""
            test_lines = [f"Thread {thread_id} line {i}" for i in range(30)]
            tests_without_shas, _ = self.parser.create_tests(
                f"test-suite-{thread_id}", f"test-pattern-{thread_id}", test_lines, None
            )
            results[thread_id] = tests_without_shas

        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_tests_worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all threads completed successfully
        self.assertEqual(len(results), 5)
        for thread_id in range(5):
            self.assertEqual(len(results[thread_id]), 1)  # One test per thread
            test_name = f"test-pattern-{thread_id}"
            self.assertEqual(len(results[thread_id][test_name]), 30)

    def test_memory_limits_with_pattern_extraction(self):
        """Test per-pattern limiting with name extraction (per unique extracted pattern)."""
        # Set up logging capture
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        logger = logging.getLogger()
        logger.addHandler(handler)
        logger.setLevel(logging.WARNING)

        try:
            # Create log with multiple different KASAN types, each appearing 35 times
            log_lines = []

            # 35 instances of slab-out-of-bounds
            for i in range(35):
                log_lines.append(
                    f"[  {18 + i}.000000] BUG: KASAN: slab-out-of-bounds in function_a+0x{i:03x}/0x660"
                )

            # 35 instances of use-after-free
            for i in range(35):
                log_lines.append(
                    f"[  {50 + i}.000000] BUG: KASAN: use-after-free in function_b+0x{i:03x}/0x456"
                )

            # 35 instances of vmalloc-out-of-bounds
            for i in range(35):
                log_lines.append(
                    f"[  {80 + i}.000000] BUG: KASAN: vmalloc-out-of-bounds in function_c+0x{i:03x}/0x789"
                )

            test_log = "\n".join(log_lines)

            # Parse the log
            self.boot_parser.parse_log(test_log, unique=True)

            # Check warnings - should have warnings for different patterns
            warning_output = log_capture.getvalue()
            warning_lines = [
                line
                for line in warning_output.split("\n")
                if "Truncated test creation" in line
            ]

            # Should have warnings for different patterns
            self.assertGreaterEqual(len(warning_lines), 3)

            # Verify different pattern types are mentioned
            all_warnings = " ".join(warning_lines)
            self.assertIn("slab-out-of-bounds", all_warnings)
            self.assertIn("use-after-free", all_warnings)
            self.assertIn("vmalloc-out-of-bounds", all_warnings)

            # Verify each warning mentions 30 tests
            for warning in warning_lines:
                self.assertIn("30 tests", warning)

        finally:
            logger.removeHandler(handler)

    def test_memory_limits_per_pattern_independence(self):
        """Test that different patterns have independent memory limits."""
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        logger = logging.getLogger()
        logger.addHandler(handler)
        logger.setLevel(logging.WARNING)

        try:
            log_lines = []

            # Add 31 KASAN reports (should trigger limit)
            for i in range(31):
                log_lines.append(
                    f"[  {10 + i}.000000] BUG: KASAN: slab-out-of-bounds in kasan_func+0x{i:03x}/0x456"
                )

            # Add 25 OOPS reports (should NOT trigger limit)
            for i in range(25):
                log_lines.append(f"[  {50 + i}.000000] Oops: 0000 [#{i + 1}] SMP")

            test_log = "\n".join(log_lines)

            # Parse the log
            self.boot_parser.parse_log(test_log, unique=True)

            # Check warnings - should have warnings for KASAN but not OOPS
            warning_output = log_capture.getvalue()
            warning_lines = [
                line
                for line in warning_output.split("\n")
                if "Truncated test creation" in line
            ]

            self.assertGreaterEqual(len(warning_lines), 1)

            # Should mention KASAN-related patterns but not OOPS
            has_kasan_warning = any(
                "kasan" in warning.lower() or "slab-out-of-bounds" in warning
                for warning in warning_lines
            )
            has_oops_warning = any(
                "oops" in warning.lower() for warning in warning_lines
            )

            self.assertTrue(has_kasan_warning, "Should have KASAN-related warning")
            self.assertFalse(has_oops_warning, "Should not have OOPS warning")

        finally:
            logger.removeHandler(handler)

    def test_memory_limits_warning_once_per_pattern(self):
        """Test that warnings are logged only once per pattern, not per occurrence."""
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        logger = logging.getLogger()
        logger.addHandler(handler)
        logger.setLevel(logging.WARNING)

        try:
            # Create 100 identical KASAN reports (way over limit)
            log_lines = []
            for i in range(100):
                log_lines.append(
                    f"[  {10 + i}.000000] BUG: KASAN: slab-out-of-bounds in test_func+0x123/0x456"
                )

            test_log = "\n".join(log_lines)

            # Parse the log
            self.boot_parser.parse_log(test_log, unique=True)

            # Check that warnings are limited, not one per occurrence
            warning_output = log_capture.getvalue()
            warning_count = warning_output.count("Truncated test creation at 30 tests")

            # Should be small number of warnings (not 100+), allowing for with/without SHAs
            self.assertLessEqual(
                warning_count,
                5,
                "Warning count should be limited, not one per occurrence",
            )
            self.assertGreaterEqual(
                warning_count, 1, "Should have at least one warning"
            )

        finally:
            logger.removeHandler(handler)


if __name__ == "__main__":
    unittest.main()

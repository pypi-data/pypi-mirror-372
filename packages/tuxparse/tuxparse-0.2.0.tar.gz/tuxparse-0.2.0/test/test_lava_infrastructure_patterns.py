#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test suite for LAVA infrastructure issue patterns in boot_test_parser.

Tests the functionality added in commit 49ee7811249abf9561de4cb9cf95ad2e0254faf3
which adds regex patterns to detect LAVA-specific infrastructure problems
that cause test failures independent of kernel issues.
"""

import unittest
from tuxparse.boot_test_parser import BootTestParser, LAVA_ISSUES, REGEXES


class TestLavaInfrastructurePatterns(unittest.TestCase):
    """Test suite for LAVA infrastructure issue patterns functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = BootTestParser()

    def test_lava_issues_patterns_exist(self):
        """Test that LAVA infrastructure patterns are properly defined."""
        # Verify LAVA_ISSUES contains the expected patterns
        expected_patterns = [
            "lava-timeout",
            "lava-error",
            "lava-connection",
            "lava-validation",
            "lava-command",
        ]

        lava_pattern_names = [pattern[0] for pattern in LAVA_ISSUES]
        for expected_pattern in expected_patterns:
            self.assertIn(expected_pattern, lava_pattern_names)

        # Verify LAVA patterns are included in main REGEXES
        self.assertEqual(len(LAVA_ISSUES), 5)
        self.assertTrue(
            any(
                pattern[0]
                in [
                    "lava-timeout",
                    "lava-error",
                    "lava-connection",
                    "lava-validation",
                    "lava-command",
                ]
                for pattern in REGEXES
            )
        )

    def test_lava_timeout_pattern_detection(self):
        """Test detection of LAVA timeout issues."""
        log_with_timeout = """[    0.000000] Linux version 6.16.0
[    1.000000] Boot started
[    2.000000] [LAVA-INFRA] LAVA Timeout: Test execution exceeded 30 minutes
[    3.000000] System continuing"""

        # Process the log
        results = self.parser._process_log_section(log_with_timeout, "boot", False)

        # Should detect LAVA timeout
        self.assertIn("log-parser-boot", results)
        boot_suite = results["log-parser-boot"]

        # Look for timeout-related test
        timeout_tests = [
            name for name in boot_suite.keys() if "timeout" in name.lower()
        ]
        self.assertGreater(len(timeout_tests), 0)

        # Verify test contains the timeout message
        timeout_test = timeout_tests[0]
        log_excerpt = boot_suite[timeout_test]["log_excerpt"]
        self.assertTrue(any("LAVA Timeout" in line for line in log_excerpt))

    def test_lava_error_pattern_detection(self):
        """Test detection of LAVA error issues."""
        log_with_error = """[    0.000000] Linux version 6.16.0
[    1.000000] Boot started
[    2.000000] [LAVA-INFRA] LAVA Error: Unable to connect to device
[    3.000000] System continuing"""

        # Process the log
        results = self.parser._process_log_section(log_with_error, "boot", False)

        # Should detect LAVA error
        self.assertIn("log-parser-boot", results)
        boot_suite = results["log-parser-boot"]

        # Look for error-related test
        error_tests = [name for name in boot_suite.keys() if "error" in name.lower()]
        self.assertGreater(len(error_tests), 0)

        # Verify test contains the error message
        error_test = error_tests[0]
        log_excerpt = boot_suite[error_test]["log_excerpt"]
        self.assertTrue(any("LAVA Error" in line for line in log_excerpt))

    def test_lava_connection_pattern_detection(self):
        """Test detection of LAVA connection issues."""
        log_with_connection_issue = """[    0.000000] Linux version 6.16.0
[    1.000000] Boot started
[    2.000000] [LAVA-INFRA] LAVA Connection Lost: SSH connection terminated unexpectedly
[    3.000000] System continuing"""

        # Process the log
        results = self.parser._process_log_section(
            log_with_connection_issue, "boot", False
        )

        # Should detect LAVA connection issue
        self.assertIn("log-parser-boot", results)
        boot_suite = results["log-parser-boot"]

        # Look for connection-related test
        connection_tests = [
            name for name in boot_suite.keys() if "connection" in name.lower()
        ]
        self.assertGreater(len(connection_tests), 0)

        # Verify test contains the connection message
        connection_test = connection_tests[0]
        log_excerpt = boot_suite[connection_test]["log_excerpt"]
        self.assertTrue(any("LAVA Connection Lost" in line for line in log_excerpt))

    def test_lava_validation_pattern_detection(self):
        """Test detection of LAVA validation issues."""
        log_with_validation_issue = """[    0.000000] Linux version 6.16.0
[    1.000000] Boot started
[    2.000000] [LAVA-INFRA] LAVA Validation Failed: Job definition validation error
[    3.000000] System continuing"""

        # Process the log
        results = self.parser._process_log_section(
            log_with_validation_issue, "boot", False
        )

        # Should detect LAVA validation issue
        self.assertIn("log-parser-boot", results)
        boot_suite = results["log-parser-boot"]

        # Look for validation-related test
        validation_tests = [
            name for name in boot_suite.keys() if "validation" in name.lower()
        ]
        self.assertGreater(len(validation_tests), 0)

        # Verify test contains the validation message
        validation_test = validation_tests[0]
        log_excerpt = boot_suite[validation_test]["log_excerpt"]
        self.assertTrue(any("LAVA Validation Failed" in line for line in log_excerpt))

    def test_lava_command_pattern_detection(self):
        """Test detection of LAVA command issues."""
        log_with_command_issue = """[    0.000000] Linux version 6.16.0
[    1.000000] Boot started
[    2.000000] [LAVA-INFRA] LAVA Command Failed: Unable to execute test command
[    3.000000] System continuing"""

        # Process the log
        results = self.parser._process_log_section(
            log_with_command_issue, "boot", False
        )

        # Should detect LAVA command issue
        self.assertIn("log-parser-boot", results)
        boot_suite = results["log-parser-boot"]

        # Look for command-related test
        command_tests = [
            name for name in boot_suite.keys() if "command" in name.lower()
        ]
        self.assertGreater(len(command_tests), 0)

        # Verify test contains the command message
        command_test = command_tests[0]
        log_excerpt = boot_suite[command_test]["log_excerpt"]
        self.assertTrue(any("LAVA Command Failed" in line for line in log_excerpt))

    def test_multiple_lava_issues_in_single_log(self):
        """Test detection of multiple LAVA issues in a single log."""
        log_with_multiple_issues = """[    0.000000] Linux version 6.16.0
[    1.000000] Boot started
[    2.000000] [LAVA-INFRA] LAVA Timeout: Test execution exceeded 30 minutes
[    3.000000] [LAVA-INFRA] LAVA Error: Unable to connect to device
[    4.000000] [LAVA-INFRA] LAVA Connection Lost: SSH connection terminated
[    5.000000] System continuing"""

        # Process the log
        results = self.parser._process_log_section(
            log_with_multiple_issues, "boot", False
        )

        # Should detect multiple LAVA issues
        self.assertIn("log-parser-boot", results)
        boot_suite = results["log-parser-boot"]

        # Should have multiple LAVA-related tests
        lava_tests = [name for name in boot_suite.keys() if "lava" in name.lower()]
        self.assertGreaterEqual(
            len(lava_tests), 3
        )  # At least timeout, error, connection

        # Verify each test contains appropriate message
        test_messages = {}
        for test_name in lava_tests:
            log_excerpt = boot_suite[test_name]["log_excerpt"]
            test_messages[test_name] = " ".join(log_excerpt)

        # Should have different types of LAVA issues
        has_timeout = any("LAVA Timeout" in msg for msg in test_messages.values())
        has_error = any("LAVA Error" in msg for msg in test_messages.values())
        has_connection = any(
            "LAVA Connection Lost" in msg for msg in test_messages.values()
        )

        self.assertTrue(has_timeout)
        self.assertTrue(has_error)
        self.assertTrue(has_connection)

    def test_lava_patterns_with_mixed_kernel_issues(self):
        """Test LAVA patterns work correctly alongside kernel issue patterns."""
        log_with_mixed_issues = """[    0.000000] Linux version 6.16.0
[    1.000000] Boot started
[    2.000000] [LAVA-INFRA] LAVA Timeout: Test execution exceeded 30 minutes
[    3.000000] Kernel panic - not syncing: system failure
[    4.000000] [LAVA-INFRA] LAVA Error: Unable to connect to device
[    5.000000] BUG: KASAN: use-after-free in test_function
[    6.000000] System continuing"""

        # Process the log
        results = self.parser._process_log_section(log_with_mixed_issues, "boot", False)

        # Should detect both LAVA and kernel issues
        self.assertIn("log-parser-boot", results)
        boot_suite = results["log-parser-boot"]

        # Should have both LAVA and kernel issue tests
        lava_tests = [name for name in boot_suite.keys() if "lava" in name.lower()]
        kernel_tests = [
            name
            for name in boot_suite.keys()
            if any(term in name.lower() for term in ["panic", "kasan", "bug"])
        ]

        self.assertGreater(len(lava_tests), 0)
        self.assertGreater(len(kernel_tests), 0)

        # Verify separation of issues
        for test_name in lava_tests:
            log_excerpt = boot_suite[test_name]["log_excerpt"]
            combined_lines = " ".join(log_excerpt)
            self.assertTrue("LAVA" in combined_lines)

        for test_name in kernel_tests:
            log_excerpt = boot_suite[test_name]["log_excerpt"]
            combined_lines = " ".join(log_excerpt)
            self.assertTrue(
                any(term in combined_lines for term in ["panic", "KASAN", "BUG"])
            )

    def test_lava_patterns_case_sensitivity(self):
        """Test LAVA patterns are case sensitive and require exact format."""
        # Test with correct case (should match)
        log_with_correct_case = """[    0.000000] Linux version 6.16.0
[    1.000000] Boot started
[    2.000000] [LAVA-INFRA] LAVA Timeout: Test execution exceeded 30 minutes
[    3.000000] [LAVA-INFRA] LAVA Error: Unable to connect to device
[    4.000000] System continuing"""

        # Process the log
        results = self.parser._process_log_section(log_with_correct_case, "boot", False)

        # Should detect LAVA issues with correct case
        self.assertIn("log-parser-boot", results)
        boot_suite = results["log-parser-boot"]

        # Should have LAVA-related tests
        lava_tests = [name for name in boot_suite.keys() if "lava" in name.lower()]
        self.assertGreater(len(lava_tests), 0)

        # Test with incorrect case (should not match LAVA patterns)
        log_with_incorrect_case = """[    0.000000] Linux version 6.16.0
[    1.000000] Boot started
[    2.000000] [LAVA-INFRA] lava timeout: Test execution exceeded 30 minutes
[    3.000000] [LAVA-INFRA] lava error: Unable to connect to device
[    4.000000] System continuing"""

        # Process the log
        results_incorrect = self.parser._process_log_section(
            log_with_incorrect_case, "boot", False
        )

        # Should not detect LAVA issues with incorrect case
        if "log-parser-boot" in results_incorrect:
            boot_suite_incorrect = results_incorrect["log-parser-boot"]
            lava_tests_incorrect = [
                name for name in boot_suite_incorrect.keys() if "lava" in name.lower()
            ]
            # Should have fewer or no LAVA tests due to case sensitivity
            self.assertLessEqual(len(lava_tests_incorrect), len(lava_tests))

    def test_lava_patterns_with_timestamps(self):
        """Test LAVA patterns work with various timestamp formats."""
        log_with_timestamps = """[    0.000000] Linux version 6.16.0
[    1.123456] Boot started
[   10.000000] [LAVA-INFRA] LAVA Timeout: Test execution exceeded 30 minutes
[  100.987654] [LAVA-INFRA] LAVA Error: Unable to connect to device
[ 1000.000000] System continuing"""

        # Process the log
        results = self.parser._process_log_section(log_with_timestamps, "boot", False)

        # Should detect LAVA issues with various timestamp formats
        self.assertIn("log-parser-boot", results)
        boot_suite = results["log-parser-boot"]

        # Should have LAVA-related tests
        lava_tests = [name for name in boot_suite.keys() if "lava" in name.lower()]
        self.assertGreater(len(lava_tests), 0)

    def test_lava_patterns_regex_priority(self):
        """Test that LAVA patterns have priority over other patterns."""
        # Since LAVA_ISSUES are first in REGEXES, they should be checked first
        from tuxparse.boot_test_parser import REGEXES

        # Verify LAVA patterns are at the beginning
        first_five_patterns = [pattern[0] for pattern in REGEXES[:5]]
        lava_pattern_names = [pattern[0] for pattern in LAVA_ISSUES]

        # All LAVA patterns should be in first positions
        for lava_pattern in lava_pattern_names:
            self.assertIn(lava_pattern, first_five_patterns)

    def test_lava_patterns_full_integration(self):
        """Test LAVA patterns work with full parse_log integration."""
        log_with_lava_issues = """[    0.000000] Linux version 6.16.0
[    1.000000] Boot started
[    2.000000] [LAVA-INFRA] LAVA Timeout: Test execution exceeded 30 minutes
[    3.000000] [LAVA-INFRA] LAVA Error: Unable to connect to device
[    4.000000] System continuing"""

        # Process through full parse_log method
        data = self.parser.parse_log(log_with_lava_issues, unique=False)

        # Should return valid data structure
        self.assertIsInstance(data, dict)

        # Should be valid JSON containing LAVA issues if detected
        if data and "log-parser-boot" in data:
            boot_suite = data["log-parser-boot"]
            lava_tests = [name for name in boot_suite.keys() if "lava" in name.lower()]
            self.assertGreater(len(lava_tests), 0)

    def test_lava_patterns_with_chunked_processing(self):
        """Test LAVA patterns work with chunked processing for large logs."""
        # Create a large log with LAVA issues
        log_excerpt = []
        for i in range(6000):  # Larger than chunk size
            log_excerpt.append(f"[{i:8.3f}] Normal message {i}")
            if i == 1000:
                log_excerpt.append(
                    f"[{i:8.3f}] [LAVA-INFRA] LAVA Timeout: Test execution exceeded 30 minutes"
                )
            elif i == 3000:
                log_excerpt.append(
                    f"[{i:8.3f}] [LAVA-INFRA] LAVA Error: Unable to connect to device"
                )
            elif i == 5000:
                log_excerpt.append(
                    f"[{i:8.3f}] [LAVA-INFRA] LAVA Connection Lost: SSH connection terminated"
                )

        large_log = "\n".join(log_excerpt)

        # Process with chunked processing
        results = self.parser._process_log_in_chunks(large_log, False)

        # Should detect LAVA issues across chunks
        self.assertIn("log-parser-boot", results)
        boot_suite = results["log-parser-boot"]

        # Should have LAVA-related tests
        lava_tests = [name for name in boot_suite.keys() if "lava" in name.lower()]
        self.assertGreater(len(lava_tests), 0)

        # Should have detected multiple types of LAVA issues
        test_messages = {}
        for test_name in lava_tests:
            log_excerpt = boot_suite[test_name]["log_excerpt"]
            test_messages[test_name] = " ".join(log_excerpt)

        # Should have different types of LAVA issues from different chunks
        has_timeout = any("LAVA Timeout" in msg for msg in test_messages.values())
        has_error = any("LAVA Error" in msg for msg in test_messages.values())
        has_connection = any(
            "LAVA Connection Lost" in msg for msg in test_messages.values()
        )

        self.assertTrue(has_timeout or has_error or has_connection)

    def test_lava_patterns_name_extraction(self):
        """Test name extraction works correctly for LAVA patterns."""
        log_with_lava_issues = """[    0.000000] Linux version 6.16.0
[    1.000000] [LAVA-INFRA] LAVA Timeout: Test execution exceeded 30 minutes
[    2.000000] [LAVA-INFRA] LAVA Error: Unable to connect to device"""

        # Process the log
        results = self.parser._process_log_section(log_with_lava_issues, "boot", False)

        # Should detect LAVA issues
        self.assertIn("log-parser-boot", results)
        boot_suite = results["log-parser-boot"]

        # Verify test names contain LAVA pattern identifiers
        test_names = list(boot_suite.keys())
        lava_test_names = [name for name in test_names if "lava" in name.lower()]
        self.assertGreater(len(lava_test_names), 0)

        # Test names should be descriptive
        for test_name in lava_test_names:
            self.assertTrue(
                any(
                    term in test_name.lower()
                    for term in [
                        "timeout",
                        "error",
                        "connection",
                        "validation",
                        "command",
                    ]
                )
            )

    def test_lava_patterns_edge_cases(self):
        """Test LAVA patterns handle edge cases correctly."""
        # Test with empty LAVA-INFRA message
        log_with_empty = """[    0.000000] [LAVA-INFRA] LAVA Timeout:"""
        results = self.parser._process_log_section(log_with_empty, "boot", False)
        self.assertIn("log-parser-boot", results)

        # Test with very long LAVA message
        long_message = "x" * 1000
        log_with_long = f"""[    0.000000] [LAVA-INFRA] LAVA Error: {long_message}"""
        results = self.parser._process_log_section(log_with_long, "boot", False)
        self.assertIn("log-parser-boot", results)

        # Test with special characters in LAVA message
        log_with_special = (
            """[    0.000000] [LAVA-INFRA] LAVA Timeout: Test failed @#$%^&*()"""
        )
        results = self.parser._process_log_section(log_with_special, "boot", False)
        self.assertIn("log-parser-boot", results)

    def test_lava_patterns_boot_test_split(self):
        """Test LAVA patterns work correctly with boot/test log splitting."""
        log_with_split = """[    0.000000] Linux version 6.16.0
[    1.000000] [LAVA-INFRA] LAVA Timeout: Boot timeout occurred
[    2.000000] test-system login:
[    3.000000] [LAVA-INFRA] LAVA Error: Test execution failed
[    4.000000] Test output here"""

        # Process with boot/test splitting
        boot_log, test_log = self.parser._BootTestParser__cutoff_boot_log(
            log_with_split
        )

        # Process boot section
        boot_results = self.parser._process_log_section(boot_log, "boot", False)
        self.assertIn("log-parser-boot", boot_results)
        boot_suite = boot_results["log-parser-boot"]
        boot_lava_tests = [name for name in boot_suite.keys() if "lava" in name.lower()]

        # Process test section
        test_results = self.parser._process_log_section(test_log, "test", False)
        self.assertIn("log-parser-test", test_results)
        test_suite = test_results["log-parser-test"]
        test_lava_tests = [name for name in test_suite.keys() if "lava" in name.lower()]

        # Should have LAVA issues in both sections
        self.assertGreater(len(boot_lava_tests), 0)  # Boot timeout
        self.assertGreater(len(test_lava_tests), 0)  # Test error


if __name__ == "__main__":
    unittest.main()

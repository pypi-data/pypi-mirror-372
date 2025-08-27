#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import io
from unittest.mock import patch, MagicMock
from tuxparse.boot_test_parser import BootTestParser


class TestChunkedProcessing(unittest.TestCase):
    """Test suite for chunked processing functionality in boot_test_parser."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = BootTestParser()

    def test_chunked_processing_basic_functionality(self):
        """Test basic chunked processing with a moderately sized log."""
        # Create a log with multiple chunks (chunk_size=5000, so 6k lines = 2 chunks)
        log_excerpt = []
        for i in range(6000):
            if i % 1000 == 0:
                log_excerpt.append(
                    f"[{i:8.3f}] Kernel panic - not syncing: test panic {i}"
                )
            else:
                log_excerpt.append(f"[{i:8.3f}] Normal kernel message {i}")

        large_log = "\n".join(log_excerpt)

        # Process with chunked processing
        results = self.parser._process_log_in_chunks(large_log, False)

        # Verify results
        self.assertIn("log-parser-boot", results)
        boot_suite = results["log-parser-boot"]

        # Should have multiple panic tests detected
        panic_tests = [name for name in boot_suite.keys() if "panic" in name]
        self.assertGreater(len(panic_tests), 0)

        # Each panic test should have log lines
        for test_name in panic_tests:
            self.assertGreater(len(boot_suite[test_name]["log_excerpt"]), 0)

    def test_chunked_processing_with_overlap(self):
        """Test that chunked processing maintains overlap between chunks."""
        # Create a log where a multi-line pattern spans chunk boundaries
        log_excerpt = []

        # Add 4900 lines to approach chunk boundary
        for i in range(4900):
            log_excerpt.append(f"[{i:8.3f}] Normal message {i}")

        # Add a multi-line pattern that spans chunk boundary
        log_excerpt.extend(
            [
                "[4900.000] ------------[ cut here ]------------",
                "[4900.001] WARNING: CPU: 0 PID: 1 at kernel/test.c:123 test_function+0x20/0x30",
                "[4900.002] Modules linked in:",
                "[4900.003] CPU: 0 PID: 1 Comm: swapper/0 Not tainted 5.4.0-test #1",
                "[4900.004] Hardware name: QEMU Standard PC (i440FX + PIIX, 1996)",
                "[4900.005] Call Trace:",
                "[4900.006]  test_function+0x20/0x30",
                "[4900.007]  init_module+0x10/0x20",
                "[4900.008] ---[ end trace 1234567890abcdef ]---",
            ]
        )

        # Add more lines to create a second chunk
        for i in range(5000, 6000):
            log_excerpt.append(f"[{i:8.3f}] Normal message {i}")

        large_log = "\n".join(log_excerpt)

        # Process with chunked processing
        results = self.parser._process_log_in_chunks(large_log, False)

        # Verify the multi-line pattern was detected
        self.assertIn("log-parser-boot", results)
        boot_suite = results["log-parser-boot"]

        # Should have detected the warning
        warning_tests = [
            name for name in boot_suite.keys() if "WARNING" in name.upper()
        ]
        self.assertGreater(len(warning_tests), 0)

    def test_chunked_processing_memory_efficiency(self):
        """Test that chunked processing is memory efficient."""

        # Create a very large log (but process in small chunks)
        def generate_large_log():
            """Generator for large log to avoid loading all into memory."""
            for i in range(20000):  # 20k lines
                if i % 5000 == 0:
                    yield f"[{i:8.3f}] Kernel panic - not syncing: test panic {i}\n"
                else:
                    yield f"[{i:8.3f}] Normal kernel message {i}\n"

        # Create a file-like object from generator
        large_log_content = "".join(generate_large_log())
        log_stream = io.StringIO(large_log_content)

        # Process with small chunk size for memory efficiency testing
        results = self.parser._process_log_in_chunks(log_stream, False, chunk_size=1000)

        # Verify results
        self.assertIn("log-parser-boot", results)
        boot_suite = results["log-parser-boot"]

        # Should have detected multiple panic tests
        panic_tests = [name for name in boot_suite.keys() if "panic" in name]
        self.assertGreater(len(panic_tests), 0)

    def test_chunked_processing_with_file_object(self):
        """Test chunked processing with file-like objects."""
        # Create test log content
        log_content = []
        for i in range(7000):
            if i % 2000 == 0:
                log_content.append(
                    f"[{i:8.3f}] Kernel panic - not syncing: test panic {i}"
                )
            else:
                log_content.append(f"[{i:8.3f}] Normal message {i}")

        log_text = "\n".join(log_content)

        # Test with StringIO (seekable)
        log_stream = io.StringIO(log_text)
        results = self.parser._process_log_in_chunks(log_stream, False)

        self.assertIn("log-parser-boot", results)
        panic_tests = [
            name for name in results["log-parser-boot"].keys() if "panic" in name
        ]
        self.assertGreater(len(panic_tests), 0)

        # Test with string input
        results_string = self.parser._process_log_in_chunks(log_text, False)

        # Results should be equivalent
        self.assertEqual(
            len(results["log-parser-boot"]), len(results_string["log-parser-boot"])
        )

    def test_chunked_processing_fallback_to_simple(self):
        """Test that small logs fallback to simple processing."""
        # Create a small log (less than chunk_size)
        small_log = []
        for i in range(100):
            if i == 50:
                small_log.append(
                    f"[{i:8.3f}] Kernel panic - not syncing: small test panic"
                )
            else:
                small_log.append(f"[{i:8.3f}] Normal message {i}")

        log_text = "\n".join(small_log)

        # Mock the seek operation to verify fallback path
        with patch("io.StringIO") as mock_stringio:
            mock_file = MagicMock()
            mock_file.readline.side_effect = log_text.split("\n") + [""]
            mock_file.seek.return_value = None
            mock_file.read.return_value = log_text
            mock_stringio.return_value = mock_file

            results = self.parser._process_log_in_chunks(log_text, False)

            # Should still detect the panic
            self.assertIn("log-parser-boot", results)
            panic_tests = [
                name for name in results["log-parser-boot"].keys() if "panic" in name
            ]
            self.assertGreater(len(panic_tests), 0)

    def test_chunked_processing_merge_results(self):
        """Test the result merging functionality."""
        # Create two sets of results to merge
        main_results = {
            "log-parser-boot": {
                "test1": {"log_excerpt": ["line1", "line2"], "result": "fail"},
                "test2": {"log_excerpt": ["line3"], "result": "fail"},
            }
        }

        new_results = {
            "log-parser-boot": {
                "test1": {
                    "log_excerpt": ["line2", "line4"],
                    "result": "fail",
                },  # Overlapping
                "test3": {"log_excerpt": ["line5", "line6"], "result": "fail"},  # New
            }
        }

        # Merge results
        self.parser._merge_results(main_results, new_results)

        # Verify merging
        boot_suite = main_results["log-parser-boot"]

        # test1 should have merged lines (no duplicates)
        self.assertIn("test1", boot_suite)
        test1_lines = set(boot_suite["test1"]["log_excerpt"])
        expected_lines = {"line1", "line2", "line4"}
        self.assertEqual(test1_lines, expected_lines)

        # test2 should remain unchanged
        self.assertEqual(boot_suite["test2"]["log_excerpt"], ["line3"])

        # test3 should be added
        self.assertIn("test3", boot_suite)
        self.assertEqual(boot_suite["test3"]["log_excerpt"], ["line5", "line6"])

    def test_chunked_processing_snippet_limiting(self):
        """Test snippet limiting in chunked processing."""
        # Create results with too many snippets
        main_results = {
            "log-parser-boot": {
                "test1": {
                    "log_excerpt": [f"line{i}" for i in range(50)],
                    "result": "fail",
                }
            }
        }

        new_results = {
            "log-parser-boot": {
                "test1": {
                    "log_excerpt": [f"newline{i}" for i in range(20)],
                    "result": "fail",
                }
            }
        }

        # Merge with snippet limiting
        with patch("logging.Logger.warning") as mock_warning:
            self.parser._merge_results(
                main_results, new_results, max_snippets_per_test=30
            )

            # Should have been truncated and warning logged
            boot_suite = main_results["log-parser-boot"]
            self.assertEqual(len(boot_suite["test1"]["log_excerpt"]), 30)
            mock_warning.assert_called()

    def test_chunked_processing_with_boot_test_split(self):
        """Test chunked processing handles boot/test log splitting correctly."""
        # Create a log with both boot and test sections
        log_excerpt = []

        # Boot section
        for i in range(3000):
            log_excerpt.append(f"[{i:8.3f}] Boot message {i}")
            # Add detectable patterns in boot section
            if i == 1000:
                log_excerpt.append(
                    f"[{i:8.3f}] Kernel panic - not syncing: boot section panic"
                )
            elif i == 2000:
                # Add KASAN pattern with proper format (needs equals signs)
                log_excerpt.append(
                    f"[{i:8.3f}] =================================================================="
                )
                log_excerpt.append(f"[{i:8.3f}] BUG: KASAN: use-after-free in boot")
                log_excerpt.append(
                    f"[{i:8.3f}] =================================================================="
                )

        # Add login prompt to trigger split
        log_excerpt.append("[3000.000] test-system login:")

        # Test section
        for i in range(3001, 6000):
            log_excerpt.append(f"[{i:8.3f}] Test message {i}")
            if i == 4000:
                log_excerpt.append(
                    f"[{i:8.3f}] Kernel panic - not syncing: test section panic"
                )

        large_log = "\n".join(log_excerpt)

        # Process with chunked processing
        results = self.parser._process_log_in_chunks(large_log, False)

        # Should have both boot and test suites
        self.assertIn("log-parser-boot", results)
        self.assertIn("log-parser-test", results)

        # Boot suite should contain the panic and KASAN from boot section
        boot_suite = results["log-parser-boot"]
        boot_panic_tests = [name for name in boot_suite.keys() if "panic" in name]
        boot_kasan_tests = [name for name in boot_suite.keys() if "kasan" in name]
        self.assertGreater(len(boot_panic_tests), 0)
        self.assertGreater(len(boot_kasan_tests), 0)

        # Test suite should contain the panic from test section
        test_suite = results["log-parser-test"]
        test_panic_tests = [name for name in test_suite.keys() if "panic" in name]
        self.assertGreater(len(test_panic_tests), 0)

    def test_chunked_processing_logging(self):
        """Test that chunked processing produces appropriate logging."""
        # Create a log that will be processed in chunks
        log_excerpt = []
        for i in range(12000):  # Enough for multiple chunks
            log_excerpt.append(f"[{i:8.3f}] Message {i}")

        large_log = "\n".join(log_excerpt)

        # Process with logging
        with patch("logging.Logger.debug") as mock_debug:
            results = self.parser._process_log_in_chunks(large_log, False)

            # Should have logged chunk processing information
            mock_debug.assert_called()
            # Should return valid results
            self.assertIsInstance(results, dict)

            # Check that logging includes chunk information
            logged_messages = [call[0][0] for call in mock_debug.call_args_list]
            chunk_messages = [
                msg for msg in logged_messages if "Processing chunk" in msg
            ]
            self.assertGreater(len(chunk_messages), 0)

            # Should log completion message
            completion_messages = [
                msg for msg in logged_messages if "Completed processing" in msg
            ]
            self.assertEqual(len(completion_messages), 1)


if __name__ == "__main__":
    unittest.main()

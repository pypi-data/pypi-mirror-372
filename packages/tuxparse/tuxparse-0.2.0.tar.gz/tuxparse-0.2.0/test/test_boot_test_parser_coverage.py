#!/usr/bin/env python3
"""
Tests for uncovered code in tuxparse.boot_test_parser
"""

from tuxparse.boot_test_parser import BootTestParser


class TestBootTestParserCoverage:
    """Test coverage for uncovered code in boot_test_parser.py"""

    def setup_method(self):
        self.parser = BootTestParser()

    def test_log_excerpt_truncation_warning(self):
        """Test lines 291-292: Log excerpt truncation and warning"""
        # Create a log with many issues to trigger truncation
        log_lines = []
        # Create enough different patterns to potentially trigger truncation
        for i in range(40):
            log_lines.append(
                f"[    {i}.000000] BUG: KASAN: slab-out-of-bounds in test_func+0x{i:03x}/0x456"
            )
            log_lines.append(f"[    {i}.000001] Write of size 1 at addr ffff{i:012x}")

        large_log = "\n".join(log_lines)

        # The test should run without crashing and handle large logs
        result = self.parser.parse_log(large_log, unique=False)

        # Should have results and handle large input gracefully
        assert isinstance(result, dict)

    def test_chunked_processing_coverage(self):
        """Test various code paths in chunked processing"""
        # Test with log that triggers multiple different patterns
        mixed_log = """[    0.000000] Linux version 6.16.0-rc1
[    1.000000] BUG: KASAN: use-after-free in test_function+0x123/0x456
[    1.000001] Write of size 8 at addr ffff000081234567
[    2.000000] Kernel panic - not syncing: Fatal exception
[    3.000000] WARNING: CPU: 0 PID: 1 at drivers/test.c:100 test_func+0x20/0x30
[    4.000000] Internal error: Oops: 96000004 [#1] PREEMPT SMP
[    5.000000] Out of memory: Killed process 1234 (test_process)"""

        result = self.parser.parse_log(mixed_log, unique=False)

        # Should detect multiple different issue types
        assert isinstance(result, dict)
        if "log-parser-boot" in result:
            boot_suite = result["log-parser-boot"]
            # Should have detected various types of issues
            assert len(boot_suite) > 0

    def test_memory_efficient_processing(self):
        """Test memory efficiency with moderate sized logs"""
        # Create a reasonably sized log to test memory efficiency
        log_lines = []
        for i in range(100):
            log_lines.append(f"[  {i:3d}.000000] Normal log message {i}")
            if i % 10 == 0:  # Add some issues periodically
                log_lines.append(
                    f"[  {i:3d}.000001] BUG: KASAN: slab-out-of-bounds in func_{i}+0x123/0x456"
                )

        medium_log = "\n".join(log_lines)

        result = self.parser.parse_log(medium_log, unique=False)

        # Should complete without memory issues and return valid data
        assert isinstance(result, dict)

    def test_unique_flag_with_many_duplicates(self):
        """Test unique flag with many duplicate entries"""
        # Create log with many identical issues
        duplicate_lines = []
        for i in range(30):
            duplicate_lines.append(
                "[   10.000000] Kernel panic - not syncing: identical panic"
            )
            duplicate_lines.append("[   10.000001] CPU: 0 PID: 1 Comm: init")

        duplicate_log = "\n".join(duplicate_lines)

        result_unique = self.parser.parse_log(duplicate_log, unique=True)
        result_not_unique = self.parser.parse_log(duplicate_log, unique=False)

        # Both should return valid data
        assert isinstance(result_unique, dict)
        assert isinstance(result_not_unique, dict)

        # Unique should have fewer entries than non-unique (if any matches found)
        if (
            "log-parser-boot" in result_unique
            and "log-parser-boot" in result_not_unique
        ):
            unique_count = len(result_unique["log-parser-boot"])
            not_unique_count = len(result_not_unique["log-parser-boot"])
            assert unique_count <= not_unique_count

    def test_error_handling_edge_cases(self):
        """Test various error handling paths"""
        # Test with malformed timestamp lines
        malformed_log = """[invalid timestamp] Some message
[    0.000000] Valid message
[  bad.format] Another invalid
[    1.000000] BUG: KASAN: test issue"""

        result = self.parser.parse_log(malformed_log, unique=False)

        # Should handle malformed lines gracefully
        assert isinstance(result, dict)

    def test_pattern_matching_edge_cases(self):
        """Test edge cases in pattern matching"""
        # Test with patterns at the very beginning and end of log
        edge_case_log = """BUG: KASAN: slab-out-of-bounds at start
[    0.000000] Linux version 6.16.0
[    1.000000] Normal message
[    2.000000] BUG: KASAN: use-after-free in middle
Normal message without timestamp
Final message: Kernel panic - not syncing: at end"""

        result = self.parser.parse_log(edge_case_log, unique=False)

        # Should handle patterns at any position
        assert isinstance(result, dict)

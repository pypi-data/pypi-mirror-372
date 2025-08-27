#!/usr/bin/env python3

"""
Additional test coverage improvements based on SQUAD patterns
Focuses on edge cases and error handling that are currently untested
"""

from tuxparse.boot_test_parser import BootTestParser
from tuxparse.build_parser import BuildParser


class TestCoverageImprovements:
    """Additional tests to improve coverage based on SQUAD patterns"""

    def setup_method(self):
        self.boot_parser = BootTestParser()
        self.build_parser = BuildParser()

    # Boot parser coverage improvements
    def test_boot_parser_with_invalid_yaml_lines(self):
        """Test boot parser with malformed YAML lines in logs_txt method"""
        malformed_yaml = """- {"dt": "2025-06-18T07:24:37.906108", "lvl": "target", "msg": "good line"}
invalid yaml line without proper format
- {"dt": "incomplete json..."""

        # This should handle malformed YAML gracefully
        result = self.boot_parser.logs_txt(malformed_yaml)
        assert isinstance(result, str)

    def test_boot_parser_logs_txt_with_missing_fields(self):
        """Test logs_txt with YAML missing required fields"""
        missing_fields = """- {"timestamp": "2025-06-18T07:24:37.906108", "level": "info", "message": "wrong fields"}
- {"dt": "2025-06-18T07:24:38.000000", "lvl": "target", "msg": "correct fields"}"""

        result = self.boot_parser.logs_txt(missing_fields)
        # Should only include the line with correct fields
        assert "correct fields" in result
        assert "wrong fields" not in result

    def test_boot_parser_logs_txt_with_non_target_feedback_levels(self):
        """Test logs_txt filtering for non-target/feedback levels"""
        mixed_levels = """- {"dt": "2025-06-18T07:24:37.906108", "lvl": "debug", "msg": "debug message"}
- {"dt": "2025-06-18T07:24:38.000000", "lvl": "target", "msg": "target message"}
- {"dt": "2025-06-18T07:24:39.000000", "lvl": "info", "msg": "info message"}
- {"dt": "2025-06-18T07:24:40.000000", "lvl": "feedback", "ns": "test", "msg": "feedback message"}"""

        result = self.boot_parser.logs_txt(mixed_levels)
        assert "target message" in result
        assert "<test> feedback message" in result
        assert "debug message" not in result
        assert "info message" not in result

    def test_boot_parser_cutoff_boot_log_no_split(self):
        """Test cutoff boot log when no split pattern is found"""
        log_without_split = """[    0.000000] Linux version 6.16.0
[    1.000000] Memory initialized
[    2.000000] System ready
[    3.000000] All done"""

        boot_log, test_log = self.boot_parser._BootTestParser__cutoff_boot_log(
            log_without_split
        )
        # Should return whole log as boot log when no split found
        assert boot_log == log_without_split
        assert test_log == ""

    def test_boot_parser_cutoff_boot_log_with_split(self):
        """Test cutoff boot log when split pattern is found"""
        log_with_split = """[    0.000000] Linux version 6.16.0
[    1.000000] Memory initialized
[    2.000000] System ready
root@device:~# test started
test output here"""

        boot_log, test_log = self.boot_parser._BootTestParser__cutoff_boot_log(
            log_with_split
        )
        assert "Linux version 6.16.0" in boot_log
        assert "test started" in test_log
        assert "test output here" in test_log

    def test_boot_parser_kernel_msgs_only(self):
        """Test kernel message extraction"""
        mixed_log = """[    0.000000] Kernel message 1
user command output
[    1.000000] Kernel message 2
more user output
[    2.000000] Another kernel message"""

        result = self.boot_parser._BootTestParser__kernel_msgs_only(mixed_log)
        lines = result.split("\n")
        kernel_lines = [line for line in lines if line.strip()]

        # Should only contain kernel messages with timestamps
        assert len(kernel_lines) == 3
        assert "Kernel message 1" in result
        assert "Kernel message 2" in result
        assert "Another kernel message" in result
        assert "user command output" not in result

    def test_boot_parser_parse_log_with_empty_content(self):
        """Test parse_log with various empty content scenarios"""
        empty_cases = [None, "", "   ", "\n\n", "\t\t"]

        for empty_content in empty_cases:
            # Should handle gracefully without crashing
            self.boot_parser.parse_log(empty_content, unique=False)

    # Build parser coverage improvements
    def test_build_parser_split_by_regex_edge_cases(self):
        """Test split_by_regex with edge cases"""
        # Empty input
        result = self.build_parser.split_by_regex("", "(a)")
        assert isinstance(result, list)

        # No matches
        result = self.build_parser.split_by_regex("bbb", "(a)")
        assert result == ["bbb"]

        # Multiple consecutive matches
        result = self.build_parser.split_by_regex("aaabbb", "(a)")
        assert len(result) > 0

    def test_build_parser_post_process_test_name_edge_cases(self):
        """Test post_process_test_name with various edge cases"""
        # Just test that it doesn't crash on various inputs
        edge_cases = [
            "",
            "   ",
            "simple",
            "with/path/elements",
            "with{braces}[brackets]",
            "builds/linux/very/deep/path.c:123",
            "///multiple///slashes///",
        ]

        for input_text in edge_cases:
            result = self.build_parser.post_process_test_name(input_text)
            assert isinstance(result, str)  # Just ensure it returns a string

    def test_build_parser_clean_suite_postfix(self):
        """Test clean_suite_postfix method"""
        # Test cases that should return None (non-silent make commands)
        invalid_cases = ["make", "make --jobs=8 --keep-going", ""]
        for input_cmd in invalid_cases:
            result = self.build_parser.clean_suite_postfix(input_cmd)
            assert result is None, f"Expected None for '{input_cmd}', got {result}"

        # Test cases that should return strings (silent make commands)
        valid_cases = [
            "make --silent",
            "make --silent config",
            "make --silent --jobs=8 modules",
        ]
        for input_cmd in valid_cases:
            result = self.build_parser.clean_suite_postfix(input_cmd)
            assert isinstance(
                result, str
            ), f"Expected string for '{input_cmd}', got {result}"

    def test_build_parser_with_no_toolchain(self):
        """Test build parser with logs missing toolchain specification"""
        log_without_toolchain = """make --silent --keep-going
/builds/linux/mm/vma.h:184:26: error: 'USER_PGTABLES_CEILING' undeclared
make[3]: *** [scripts/Makefile.build:243: mm/filemap.o] Error 1"""

        data = self.build_parser.parse_log(log_without_toolchain, unique=False)

        # Test data structure directly - should handle logs without toolchain gracefully
        assert isinstance(data, dict), "Should return valid data structure"
        # Should not crash even without toolchain specification

    def test_build_parser_with_mixed_toolchain_output(self):
        """Test build parser with mixed GCC and Clang output"""
        mixed_log = """--toolchain=gcc
gcc: error: some gcc error
--toolchain=clang
clang: error: some clang error"""

        data = self.build_parser.parse_log(mixed_log, unique=False)

        # Should handle mixed toolchain logs without crashing
        assert isinstance(data, dict)

    def test_build_parser_with_very_large_line_count(self):
        """Test build parser performance with large log"""
        # Create a log with many lines to test chunking behavior
        large_log = "--toolchain=gcc\n"
        large_log += "make --silent\n" * 1000  # Many make lines
        large_log += "/path/file.c:1:1: error: test error\n" * 100  # Many errors

        data = self.build_parser.parse_log(large_log, unique=False)

        # Test data structure directly - should handle large logs efficiently
        assert isinstance(
            data, dict
        ), "Should return valid data structure for large logs"
        # Should detect errors in large logs
        assert data, "Should return non-empty data for large logs with errors"
        # Should have created build parser results
        build_keys = [k for k in data.keys() if k.startswith("log-parser-build")]
        assert len(build_keys) > 0, "Should create build parser results for large logs"
        build_tests = data[build_keys[0]]
        # Should detect some errors from the test error lines
        assert len(build_tests) > 0, "Should detect errors in large log"

    # Error handling and resilience tests
    def test_unicode_handling_in_log_content(self):
        """Test handling of Unicode characters in log content"""
        unicode_log = """[    0.000000] Kernel: démarrage système
[    1.000000] Mémoire: 初期化完了
[    2.000000] BUG: KASAN: 使用後解放 in função_teste"""

        data = self.boot_parser.parse_log(unicode_log, unique=False)

        # Test data structure directly - should handle Unicode gracefully
        assert isinstance(
            data, dict
        ), "Should return valid data structure with Unicode content"
        # Should detect KASAN error even with Unicode characters
        assert data, "Should return data for Unicode log with KASAN error"
        assert (
            "log-parser-boot" in data
        ), "Should create boot parser results for Unicode KASAN log"
        boot_tests = data["log-parser-boot"]
        kasan_tests = [name for name in boot_tests.keys() if "kasan" in name.lower()]
        assert len(kasan_tests) > 0, "Should detect KASAN even with Unicode characters"

    def test_extremely_long_lines(self):
        """Test handling of extremely long log lines"""
        very_long_line = (
            "[    0.000000] " + "x" * 10000 + " BUG: KASAN: very long error message"
        )

        data = self.boot_parser.parse_log(very_long_line, unique=False)

        # Test data structure directly - should handle very long lines without crashing
        assert isinstance(
            data, dict
        ), "Should return valid data structure with very long lines"
        # Should still detect KASAN error despite long line
        assert data, "Should return data for very long line with KASAN error"
        assert (
            "log-parser-boot" in data
        ), "Should create boot parser results for very long KASAN line"
        boot_tests = data["log-parser-boot"]
        kasan_tests = [name for name in boot_tests.keys() if "kasan" in name.lower()]
        assert len(kasan_tests) > 0, "Should detect KASAN even in very long lines"

    def test_memory_efficiency_with_repeated_patterns(self):
        """Test memory efficiency with many repeated error patterns"""
        # Create log with many identical errors to test deduplication
        repeated_log = "--toolchain=gcc\n"
        repeated_log += "/path/file.c:1:1: error: same error\n" * 500

        data = self.build_parser.parse_log(repeated_log, unique=True)

        # Should handle repeated patterns efficiently with unique=True without crashing
        assert isinstance(data, dict)

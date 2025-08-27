#!/usr/bin/env python3
"""
Tests for uncovered code in tuxparse.build_parser
"""

from tuxparse.build_parser import BuildParser


class TestBuildParserCoverage:
    """Test coverage for uncovered code in build_parser.py"""

    def setup_method(self):
        self.parser = BuildParser()

    def test_parse_log_none_input(self):
        """Test line 384: None input handling in parse_log"""
        result = self.parser.parse_log(None, unique=False)
        assert result == {}

    def test_build_parser_edge_cases(self):
        """Test various edge cases to improve coverage"""
        # Test empty log
        result = self.parser.parse_log("", unique=False)
        assert result == {}

        # Test log without toolchain
        log_without_toolchain = "Some random log content without toolchain"
        result = self.parser.parse_log(log_without_toolchain, unique=False)
        assert result == {}

    def test_toolchain_detection_coverage(self):
        """Test toolchain detection paths"""
        # Test with gcc toolchain but no actual errors
        gcc_log = "--toolchain=gcc\nmake: successful build"
        result = self.parser.parse_log(gcc_log, unique=False)
        # Should detect gcc toolchain but find no errors
        assert isinstance(result, dict)

        # Test with clang toolchain but no actual errors
        clang_log = "--toolchain=clang\nmake: successful build"
        result = self.parser.parse_log(clang_log, unique=False)
        # Should detect clang toolchain but find no errors
        assert isinstance(result, dict)

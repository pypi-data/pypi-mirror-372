#!/usr/bin/env python3
"""
Tests for uncovered code in tuxparse.test_parser
"""

import io
from unittest.mock import patch
from tuxparse.test_parser import TestParser


class TestTestParserCoverage:
    """Test coverage for uncovered code in test_parser.py"""

    def setUp(self):
        self.parser = TestParser()

    def test_process_test_suites_nested_recursion(self):
        """Test lines 34-45: Recursive processing of nested test suites"""
        parser = TestParser()

        # Test data with nested structure and proper starttc/endtc
        test_suite = {
            "test1": {
                "starttc": 1,
                "endtc": 3,
                "nested_suite": {"starttc": 2, "endtc": 2, "result": "pass"},
            },
            "test2": {"starttc": 4, "endtc": 6, "result": "fail"},
        }

        log_excerpt = [
            (1, "message 1", 1),
            (2, "message 2", 2),
            (3, "message 3", 3),
            (4, "message 4", 4),
            (5, "message 5", 5),
            (6, "message 6", 6),
        ]

        parser.process_test_suites(test_suite, log_excerpt)

        # Verify log excerpts were added correctly
        assert "log_excerpt" in test_suite["test1"]
        assert len(test_suite["test1"]["log_excerpt"]) == 3
        assert test_suite["test1"]["log_excerpt"] == [
            "message 1",
            "message 2",
            "message 3",
        ]

        # Verify nested suite was processed
        assert "log_excerpt" in test_suite["test1"]["nested_suite"]
        assert test_suite["test1"]["nested_suite"]["log_excerpt"] == ["message 2"]

        # Verify second test
        assert "log_excerpt" in test_suite["test2"]
        assert test_suite["test2"]["log_excerpt"] == [
            "message 4",
            "message 5",
            "message 6",
        ]

    def test_process_test_suites_invalid_starttc_endtc_types(self):
        """Test that non-integer starttc/endtc are skipped"""
        parser = TestParser()

        test_suite = {
            "test1": {
                "starttc": "invalid",  # String instead of int
                "endtc": 3,
                "result": "pass",
            },
            "test2": {
                "starttc": 1,
                "endtc": "invalid",  # String instead of int
                "result": "pass",
            },
        }

        log_excerpt = [(1, "message 1", 1), (2, "message 2", 2)]

        parser.process_test_suites(test_suite, log_excerpt)

        # Neither test should have log_excerpt since starttc/endtc are invalid types
        assert "log_excerpt" not in test_suite["test1"]
        assert "log_excerpt" not in test_suite["test2"]

    def test_parse_log_none_input(self):
        """Test lines 48-50: None input handling"""
        parser = TestParser()

        with patch("tuxparse.test_parser.logger") as mock_logger:
            result = parser.parse_log(None, unique=False)

            assert result == {}
            mock_logger.error.assert_called_once_with("need a log file")

    def test_parse_log_empty_log_file(self):
        """Test lines 59-61: Empty log file handling"""
        parser = TestParser()

        with patch("tuxparse.test_parser.logger") as mock_logger:
            # Test with empty string
            result = parser.parse_log("", unique=False)

            assert result == {}
            mock_logger.error.assert_called_once_with("log file is empty")

    def test_parse_log_empty_file_object(self):
        """Test empty file object input"""
        parser = TestParser()

        with patch("tuxparse.test_parser.logger") as mock_logger:
            # Test with empty file object
            empty_file = io.StringIO("")
            result = parser.parse_log(empty_file, unique=False)

            assert result == {}
            mock_logger.error.assert_called_once_with("log file is empty")

    def test_parse_log_invalid_yaml_entry_with_valueerror(self):
        """Test lines 67-73: ValueError handling in YAML parsing"""
        parser = TestParser()

        # Create YAML with entry that will cause ValueError
        yaml_content = """- dt: invalid_timestamp
  msg: 'test message'
  level: info"""

        with patch("builtins.print"):
            with patch("tuxparse.test_parser.yaml.load") as mock_yaml_load:
                # Mock yaml.load to return data that will cause ValueError
                mock_yaml_load.return_value = [
                    {
                        "dt": "invalid_timestamp",
                        "msg": "test message",
                        "_line_number": 1,
                    }
                ]

                # Mock the line parsing to raise ValueError
                with patch.object(parser, "process_test_suites"):
                    result = parser.parse_log(yaml_content, unique=False)

                    # Should still return a dict even with errors
                    assert isinstance(result, dict)

    def test_process_test_suites_non_dict_values(self):
        """Test that non-dict values in test suite are skipped"""
        parser = TestParser()

        test_suite = {
            "test1": "not_a_dict",  # String value, should be skipped
            "test2": 123,  # Number value, should be skipped
            "test3": {  # Valid dict, should be processed
                "starttc": 1,
                "endtc": 1,
                "result": "pass",
            },
        }

        log_excerpt = [(1, "message 1", 1)]

        parser.process_test_suites(test_suite, log_excerpt)

        # Only test3 should have log_excerpt
        assert "log_excerpt" not in str(test_suite["test1"])  # String, no log_excerpt
        assert "log_excerpt" not in str(test_suite["test2"])  # Number, no log_excerpt
        assert "log_excerpt" in test_suite["test3"]  # Dict, has log_excerpt

    def test_parse_log_yaml_parsing_with_special_entries(self):
        """Test YAML parsing with entries missing required fields"""
        parser = TestParser()

        yaml_content = """- dt: "2023-01-01 00:00:00"
  msg: 'valid message'
  level: info
- missing_dt: true
  msg: 'invalid entry - no dt'
- dt: "2023-01-01 00:00:01"
  missing_msg: true"""

        result = parser.parse_log(yaml_content, unique=False)

        # Should return dict even with some invalid entries
        assert isinstance(result, dict)

    def test_parse_log_file_object_input(self):
        """Test file object input processing"""
        parser = TestParser()

        yaml_content = """- dt: "2023-01-01 00:00:00"
  msg: 'test message'
  results:
    test1: pass"""

        file_obj = io.StringIO(yaml_content)
        result = parser.parse_log(file_obj, unique=False)

        assert isinstance(result, dict)

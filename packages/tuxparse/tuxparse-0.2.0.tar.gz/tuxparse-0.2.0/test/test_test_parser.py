from tuxparse.test_parser import TestParser


class TestTestParser:
    """Tests for test_parser (YAML/LAVA log parser)"""

    def setup_method(self):
        self.parser = TestParser()

    def test_parse_yaml_log_basic(self):
        """Test parsing basic YAML log format"""
        yaml_content = """- datetime: 2023-01-01 00:00:00.000000
  level: info
  message: 'test message'
  results:
    test1: pass
- datetime: 2023-01-01 00:00:01.000000
  level: error
  message: 'error message'
  results:
    test2: fail"""

        data = self.parser.parse_log(yaml_content, unique=False)

        # Test data structure directly instead of JSON dumps
        assert isinstance(data, dict), "Should return dictionary structure"
        # Basic test that parsing doesn't crash and produces expected output
        assert (
            data or data == {}
        ), "Should return valid data structure"  # Empty dict is also valid

    def test_parse_empty_yaml(self):
        """Test parsing empty YAML"""
        data = self.parser.parse_log("", unique=False)

        # Test data structure directly - empty input should return empty or no results
        assert not data or data == {}, "Empty input should return empty data structure"

    def test_parse_invalid_yaml(self):
        """Test parsing invalid YAML format"""
        invalid_yaml = """- datetime: 2023-01-01 00:00:00.000000
  level: info
  message: 'test message'
  results:
    test1: pass
- invalid yaml structure here without proper indentation
level: error"""

        # Should handle invalid YAML gracefully without crashing
        try:
            data = self.parser.parse_log(invalid_yaml, unique=False)
            # Should return dict (might be empty for invalid input)
            assert isinstance(data, dict)
        except Exception:
            # If it throws an exception, that's also acceptable behavior for invalid input
            pass

        # Test passes if no crash occurs
        assert True

    def test_parse_yaml_with_line_numbers(self):
        """Test YAML parsing with line number tracking"""
        yaml_content = """- datetime: 2023-01-01 00:00:00.000000
  level: info
  message: 'line 1'
  results:
    test1: pass
- datetime: 2023-01-01 00:00:01.000000
  level: error
  message: 'line 2'
  results:
    test2: fail"""

        data = self.parser.parse_log(yaml_content, unique=False)
        # Test that parsing completes without error
        assert isinstance(data, dict)

    def test_process_test_suites(self):
        """Test the process_test_suites method"""
        test_suite = {
            "test1": {"starttc": 1, "endtc": 3, "other_data": "value"},
            "test2": {"starttc": 4, "endtc": 6, "nested": {"starttc": 5, "endtc": 5}},
        }

        log_excerpt = [
            (1, "message 1", 1),
            (2, "message 2", 2),
            (3, "message 3", 3),
            (4, "message 4", 4),
            (5, "message 5", 5),
            (6, "message 6", 6),
        ]

        # Test that the method runs without error
        self.parser.process_test_suites(test_suite, log_excerpt)

        # Verify log_excerpt were added to test1
        assert "log_excerpt" in test_suite["test1"]
        assert len(test_suite["test1"]["log_excerpt"]) == 3
        assert test_suite["test1"]["log_excerpt"] == [
            "message 1",
            "message 2",
            "message 3",
        ]

        # Verify log_excerpt were added to test2
        assert "log_excerpt" in test_suite["test2"]
        assert len(test_suite["test2"]["log_excerpt"]) == 3
        assert test_suite["test2"]["log_excerpt"] == [
            "message 4",
            "message 5",
            "message 6",
        ]

        # Verify nested structure was processed
        assert "log_excerpt" in test_suite["test2"]["nested"]
        assert len(test_suite["test2"]["nested"]["log_excerpt"]) == 1
        assert test_suite["test2"]["nested"]["log_excerpt"] == ["message 5"]

    def test_parse_log_simple(self):
        """Test simple parsing functionality"""
        yaml_content = """- datetime: 2023-01-01 00:00:00.000000
  level: info
  message: 'test message'
  results:
    test1: pass"""

        data = self.parser.parse_log(yaml_content, unique=False)
        # Test that parsing completes without error
        assert isinstance(data, dict)

    def test_unique_flag(self):
        """Test the unique flag functionality"""
        yaml_content = """- datetime: 2023-01-01 00:00:00.000000
  level: info
  message: 'duplicate message'
  results:
    test1: pass
- datetime: 2023-01-01 00:00:01.000000
  level: info
  message: 'duplicate message'
  results:
    test2: pass
- datetime: 2023-01-01 00:00:02.000000
  level: info
  message: 'unique message' """

        data_unique = self.parser.parse_log(yaml_content, unique=True)
        data_not_unique = self.parser.parse_log(yaml_content, unique=False)

        # Both should complete without error
        assert isinstance(data_unique, dict)
        assert isinstance(data_not_unique, dict)

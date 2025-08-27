#!/usr/bin/env python3
"""
Tests for uncovered code in tuxparse.__main__
"""

import io
import json
import os
import pytest
import tempfile
from unittest.mock import MagicMock, patch
from tuxparse.__main__ import _is_lava_yaml_format, main, parse_args
from tuxparse.__main__ import start


class TestMainCoverage:
    """Test coverage for uncovered code in __main__.py"""

    def test_parse_args_no_stdin_input_error(self):
        """Test line 73: Error when no input provided via stdin"""
        # Mock sys.stdin.isatty() to return True (interactive terminal)
        with patch("sys.stdin") as mock_stdin:
            mock_stdin.isatty.return_value = True
            mock_stdin.configure_mock(**{"isatty.return_value": True})

            with patch("sys.argv", ["tuxparse", "--log-parser", "build"]):
                with pytest.raises(SystemExit):
                    parse_args()

    def test_is_lava_yaml_format_exception_handling_oserror(self):
        """Test lines 84-86: OSError exception handling in _is_lava_yaml_format"""
        mock_file = MagicMock()
        mock_file.readline.side_effect = OSError("Test OS error")

        result = _is_lava_yaml_format(mock_file)
        assert result is False

    def test_is_lava_yaml_format_exception_handling_unsupported_operation(self):
        """Test lines 84-86: UnsupportedOperation in _is_lava_yaml_format"""
        mock_file = MagicMock()
        mock_file.readline.side_effect = io.UnsupportedOperation(
            "Test unsupported operation"
        )

        result = _is_lava_yaml_format(mock_file)
        assert result is False

    def test_is_lava_yaml_format_exception_handling_general(self):
        """Test lines 87-89: General exception handling in _is_lava_yaml_format"""
        mock_file = MagicMock()
        mock_file.readline.side_effect = Exception("Test general exception")

        result = _is_lava_yaml_format(mock_file)
        assert result is False

    def test_main_debug_logging(self):
        """Test line 96: Debug logging setup"""
        test_log = "--toolchain=gcc\nmake: test"

        with patch("sys.argv", ["tuxparse", "--log-parser", "build", "--debug"]):
            with patch("sys.stdin", io.StringIO(test_log)):
                with patch("tuxparse.__main__.logger") as mock_logger:
                    try:
                        main()
                    except SystemExit:
                        pass
                    mock_logger.setLevel.assert_called_once()

    def test_main_lava_yaml_processing(self):
        """Test lines 102-115: LAVA YAML processing"""
        lava_yaml_content = """- {"dt": "2025-01-01T00:00:00.000000", "lvl": "target", "msg": "[    0.000000] Linux version 6.16.0"}"""

        with patch("sys.argv", ["tuxparse", "--log-parser", "boot_test"]):
            with patch("sys.stdin", io.StringIO(lava_yaml_content)):
                # Mock _is_lava_yaml_format to return True
                with patch("tuxparse.__main__._is_lava_yaml_format", return_value=True):
                    # Mock the logs_txt method
                    with patch(
                        "tuxparse.boot_test_parser.BootTestParser.logs_txt",
                        return_value="processed content",
                    ) as mock_logs_txt:
                        # Mock file writing
                        with patch("builtins.open", create=True) as mock_open:
                            try:
                                result = main()
                                assert result == 0
                                mock_logs_txt.assert_called_once()
                                mock_open.assert_called()
                            except SystemExit as e:
                                assert e.code == 0

    def test_main_lava_yaml_processing_exception(self):
        """Test lines 113-115: LAVA YAML processing exception handling"""
        lava_yaml_content = (
            """- {"dt": "2025-01-01T00:00:00.000000", "lvl": "target", "msg": "test"}"""
        )

        with patch("sys.argv", ["tuxparse", "--log-parser", "boot_test"]):
            with patch("sys.stdin", io.StringIO(lava_yaml_content)):
                with patch("tuxparse.__main__._is_lava_yaml_format", return_value=True):
                    # Make logs_txt raise an exception
                    with patch(
                        "tuxparse.boot_test_parser.BootTestParser.logs_txt",
                        side_effect=Exception("Test error"),
                    ):
                        with patch("tuxparse.__main__.logger") as mock_logger:
                            result = main()
                            assert result == 1
                            mock_logger.error.assert_called()

    def test_main_result_file_creation(self):
        """Test lines 123-130: Result file creation and merging"""
        test_log = "--toolchain=gcc\n/builds/linux/test.c:1:1: error: test error"

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_file:
            result_file = temp_file.name
            # Write existing JSON content
            temp_file.write('{"existing": "data"}')

        try:
            with patch(
                "sys.argv",
                ["tuxparse", "--log-parser", "build", "--result-file", result_file],
            ):
                with patch("sys.stdin", io.StringIO(test_log)):
                    try:
                        result = main()
                        assert result == 0
                    except SystemExit as e:
                        assert e.code == 0

                    # Check that file was updated
                    with open(result_file, "r") as f:
                        data = json.load(f)
                        assert "existing" in data
        finally:
            os.unlink(result_file)

    def test_main_result_file_new_file(self):
        """Test result file creation when file doesn't exist"""
        test_log = "--toolchain=gcc\n/builds/linux/test.c:1:1: error: test error"

        with tempfile.NamedTemporaryFile(suffix=".json", delete=True) as temp_file:
            result_file = temp_file.name
        # File is now deleted

        try:
            with patch(
                "sys.argv",
                ["tuxparse", "--log-parser", "build", "--result-file", result_file],
            ):
                with patch("sys.stdin", io.StringIO(test_log)):
                    try:
                        result = main()
                        assert result == 0
                    except SystemExit as e:
                        assert e.code == 0

                    # Check that file was created
                    assert os.path.exists(result_file)
                    with open(result_file, "r") as f:
                        data = json.load(f)
                        assert isinstance(data, dict)
        finally:
            if os.path.exists(result_file):
                os.unlink(result_file)

    def test_main_system_exit_handling(self):
        """Test lines 132-134: SystemExit handling"""
        with patch("sys.argv", ["tuxparse", "--log-parser", "build"]):
            with patch("sys.stdin", io.StringIO("test")):
                with patch("tuxparse.__main__.parse_args", side_effect=SystemExit(2)):
                    with pytest.raises(SystemExit) as exc_info:
                        main()
                    assert exc_info.value.code == 2

    def test_start_function(self):
        """Test line 139: start() function when __name__ == '__main__'"""
        # This tests the start() function path
        with patch("tuxparse.__main__.__name__", "__main__"):
            with patch("tuxparse.__main__.main", return_value=0) as mock_main:
                with patch("sys.exit") as mock_exit:
                    start()
                    mock_main.assert_called_once()
                    mock_exit.assert_called_once_with(0)

    def test_result_file_empty_content(self):
        """Test result file handling when existing file is empty"""
        test_log = "--toolchain=gcc\n/builds/linux/test.c:1:1: error: test error"

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_file:
            result_file = temp_file.name
            # Write empty content
            temp_file.write("")

        try:
            with patch(
                "sys.argv",
                ["tuxparse", "--log-parser", "build", "--result-file", result_file],
            ):
                with patch("sys.stdin", io.StringIO(test_log)):
                    try:
                        result = main()
                        assert result == 0
                    except SystemExit as e:
                        assert e.code == 0

                    # Check that file was updated with new data only
                    with open(result_file, "r") as f:
                        data = json.load(f)
                        assert isinstance(data, dict)
        finally:
            os.unlink(result_file)

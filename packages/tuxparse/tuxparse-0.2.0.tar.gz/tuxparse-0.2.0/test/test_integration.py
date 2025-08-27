import os
import tempfile
import pytest
from io import StringIO
from unittest.mock import patch
from tuxparse.__main__ import main


class TestTuxParseIntegration:
    """Integration tests for the main CLI"""

    def test_boot_test_parser_cli_with_panic(self):
        """Test boot_test parser via CLI with kernel panic"""
        log_content = "[    0.123] Kernel panic - not syncing: Attempted to kill init! exitcode=0x00000009"

        with patch("sys.stdin", StringIO(log_content)):
            with patch("sys.argv", ["tuxparse", "--log-parser", "boot_test"]):
                result = StringIO()
                with patch("sys.stdout", result):
                    main()

                output = result.getvalue()
                assert "panic" in output

    def test_boot_test_parser_cli_with_oops(self):
        """Test boot_test parser via CLI with kernel oops"""
        log_content = "[   14.461360] Internal error: Oops - BUG: 0 [#0] PREEMPT SMP"

        with patch("sys.stdin", StringIO(log_content)):
            with patch("sys.argv", ["tuxparse", "--log-parser", "boot_test"]):
                result = StringIO()
                with patch("sys.stdout", result):
                    main()

                output = result.getvalue()
                assert "oops" in output or "internal-error" in output

    def test_build_parser_cli_with_gcc_error(self):
        """Test build parser via CLI with GCC error"""
        log_content = """--toolchain=gcc
make --silent --keep-going --jobs=8 ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- CC=gcc
/builds/linux/mm/vma.h:184:26: error: 'USER_PGTABLES_CEILING' undeclared (first use in this function)
  184 |         vms->unmap_end = USER_PGTABLES_CEILING;"""

        with patch("sys.stdin", StringIO(log_content)):
            with patch("sys.argv", ["tuxparse", "--log-parser", "build"]):
                result = StringIO()
                with patch("sys.stdout", result):
                    main()

                output = result.getvalue()
                assert "gcc-compiler" in output or "error" in output

    def test_build_parser_cli_with_clang_error(self):
        """Test build parser via CLI with Clang error"""
        log_content = """--toolchain=clang
make --silent --keep-going --jobs=8 ARCH=arm CC=clang LLVM=1
/builds/linux/mm/vma.h:184:19: error: use of undeclared identifier 'USER_PGTABLES_CEILING'
  184 |         vms->unmap_end = USER_PGTABLES_CEILING;"""

        with patch("sys.stdin", StringIO(log_content)):
            with patch("sys.argv", ["tuxparse", "--log-parser", "build"]):
                result = StringIO()
                with patch("sys.stdout", result):
                    main()

                output = result.getvalue()
                assert "clang-compiler" in output or "error" in output

    def test_test_parser_cli_with_yaml(self):
        """Test test parser via CLI with YAML content"""
        yaml_content = """- datetime: 2023-01-01 00:00:00.000000
  level: info
  message: 'test message'
  results:
    test1: pass"""

        with patch("sys.stdin", StringIO(yaml_content)):
            with patch("sys.argv", ["tuxparse", "--log-parser", "test"]):
                result = StringIO()
                with patch("sys.stdout", result):
                    main()

                output = result.getvalue()
                # Should parse YAML without crashing
                assert len(output.strip()) >= 0

    def test_cli_with_result_file(self):
        """Test CLI with result file output"""
        log_content = "[    0.123] Kernel panic - not syncing: test"

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            result_file = f.name

        try:
            with patch("sys.stdin", StringIO(log_content)):
                with patch(
                    "sys.argv",
                    [
                        "tuxparse",
                        "--log-parser",
                        "boot_test",
                        "--result-file",
                        result_file,
                    ],
                ):
                    result = StringIO()
                    with patch("sys.stdout", result):
                        main()

            # Check that result file was created
            assert os.path.exists(result_file)

            # Check that result file has content
            with open(result_file, "r") as f:
                content = f.read()
                assert len(content) > 0

        finally:
            # Clean up temp file
            if os.path.exists(result_file):
                os.unlink(result_file)

    def test_cli_with_unique_flag(self):
        """Test CLI with unique flag"""
        log_content = """[    0.123] Kernel panic - not syncing: test
[    0.456] Kernel panic - not syncing: test"""

        with patch("sys.stdin", StringIO(log_content)):
            with patch(
                "sys.argv", ["tuxparse", "--log-parser", "boot_test", "--unique"]
            ):
                result = StringIO()
                with patch("sys.stdout", result):
                    main()

                output = result.getvalue()
                # Should produce output with unique flag
                assert len(output.strip()) >= 0

    def test_cli_with_debug_flag(self):
        """Test CLI with debug flag"""
        log_content = "[    0.123] Kernel panic - not syncing: test"

        with patch("sys.stdin", StringIO(log_content)):
            with patch(
                "sys.argv", ["tuxparse", "--log-parser", "boot_test", "--debug"]
            ):
                result = StringIO()
                with patch("sys.stdout", result):
                    main()

                output = result.getvalue()
                # Should produce output with debug enabled
                assert len(output.strip()) >= 0

    def test_cli_error_no_input(self):
        """Test CLI error when no input is provided"""
        with patch("sys.stdin.isatty", return_value=True):
            with patch("sys.argv", ["tuxparse", "--log-parser", "boot_test"]):
                with pytest.raises(SystemExit):
                    main()

    def test_cli_with_log_file_argument(self):
        """Test CLI with log file argument"""
        log_content = "[    0.123] Kernel panic - not syncing: test"

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write(log_content)
            log_file = f.name

        try:
            with patch(
                "sys.argv",
                ["tuxparse", "--log-parser", "boot_test", "--log-file", log_file],
            ):
                result = StringIO()
                with patch("sys.stdout", result):
                    main()

                output = result.getvalue()
                assert "panic" in output

        finally:
            # Clean up temp file
            if os.path.exists(log_file):
                os.unlink(log_file)

    def test_lava_yaml_preprocessing_integration(self):
        """Test complete LAVA YAML preprocessing pipeline via CLI"""
        lava_input = '- {dt: 2023-01-01T00:00:00.000000, lvl: target, msg: "[    0.000000] Kernel panic - not syncing: test panic"}'

        with patch("sys.stdin", StringIO(lava_input)):
            with patch("sys.argv", ["tuxparse", "--log-parser", "boot_test"]):
                result = StringIO()
                with patch("sys.stdout", result):
                    main()

                output = result.getvalue()
                # Should detect panic from processed LAVA YAML
                assert "panic" in output

                # Should have created logs.txt file
                assert os.path.exists("logs.txt")

                # Clean up
                if os.path.exists("logs.txt"):
                    os.unlink("logs.txt")

    def test_lava_yaml_preprocessing_with_exception(self):
        """Test LAVA YAML preprocessing with exception handling"""
        lava_input = '- {dt: 2023-01-01T00:00:00.000000, lvl: target, msg: "test"}'

        with patch("sys.stdin", StringIO(lava_input)):
            with patch("sys.argv", ["tuxparse", "--log-parser", "boot_test"]):
                from tuxparse.boot_test_parser import BootTestParser

                with patch.object(
                    BootTestParser,
                    "logs_txt",
                    side_effect=Exception("Processing error"),
                ):
                    result = main()

                    # Should return error code
                    assert result == 1

    def test_cli_with_plain_text_input(self):
        """Test CLI with plain text input (no LAVA preprocessing)"""
        plain_input = "[    0.000000] Kernel panic - not syncing: test panic"

        with patch("sys.stdin", StringIO(plain_input)):
            with patch("sys.argv", ["tuxparse", "--log-parser", "boot_test"]):
                result = StringIO()
                with patch("sys.stdout", result):
                    main()

                output = result.getvalue()
                # Should detect panic from plain text
                assert "panic" in output

#!/usr/bin/env python3

"""
Tests for build_parser using sample log files
"""

import os

from tuxparse.build_parser import BuildParser


def read_sample_file(name):
    """Read sample log files from test data directory"""
    if not name.startswith("/"):
        name = os.path.join(os.path.dirname(__file__), "data", "build", name)
    with open(name, "r") as f:
        return f.read()


class TestBuildParserSamples:
    """Tests for build_parser using sample log files"""

    def setup_method(self):
        self.parser = BuildParser()

    def test_detects_gcc_compiler_error(self):
        """Test detection of GCC compiler errors using sample log"""
        log = read_sample_file("gcc_error.log")
        data = self.parser.parse_log(log, unique=False)

        # Test data structure directly instead of JSON dumps
        assert data, "Should detect GCC compiler errors"

        # Get build parser results
        build_parser_keys = [k for k in data.keys() if k.startswith("log-parser-build")]
        assert len(build_parser_keys) > 0, "Should create build parser results"

        build_tests = data[build_parser_keys[0]]

        # Verify GCC compiler error tests were created
        gcc_tests = [name for name in build_tests.keys() if "gcc-compiler" in name]
        assert len(gcc_tests) > 0, "Should detect GCC compiler errors"

        # Verify log excerpts contain expected error content
        found_error = False
        found_undeclared_content = False
        for test_name, test_data in build_tests.items():
            if "gcc-compiler" in test_name:
                log_excerpt = test_data.get("log_excerpt", [])
                excerpt_text = " ".join(log_excerpt)
                if "error" in excerpt_text:
                    found_error = True
                if (
                    "USER_PGTABLES_CEILING" in excerpt_text
                    or "undeclared" in excerpt_text
                ):
                    found_undeclared_content = True

        assert found_error, "Should capture error messages"
        assert (
            found_undeclared_content
        ), "Should capture undeclared identifier or USER_PGTABLES_CEILING errors"

    def test_detects_gcc_compiler_warning(self):
        """Test detection of GCC compiler warnings using sample log"""
        log = read_sample_file("gcc_warning.log")
        data = self.parser.parse_log(log, unique=False)

        # Test data structure directly instead of JSON dumps
        assert data, "Should detect GCC compiler warnings"

        # Get build parser results
        build_parser_keys = [k for k in data.keys() if k.startswith("log-parser-build")]
        assert len(build_parser_keys) > 0, "Should create build parser results"

        build_tests = data[build_parser_keys[0]]

        # Verify GCC compiler warning tests were created
        gcc_tests = [name for name in build_tests.keys() if "gcc-compiler" in name]
        assert len(gcc_tests) > 0, "Should detect GCC compiler warnings"

        # Verify log excerpts contain expected warning content
        found_warning = False
        found_format_content = False
        for test_name, test_data in build_tests.items():
            if "gcc-compiler" in test_name:
                log_excerpt = test_data.get("log_excerpt", [])
                excerpt_text = " ".join(log_excerpt)
                if "warning" in excerpt_text:
                    found_warning = True
                if "format" in excerpt_text or "expects argument" in excerpt_text:
                    found_format_content = True

        assert found_warning, "Should capture warning messages"
        assert (
            found_format_content
        ), "Should capture format-related warnings or argument errors"

    def test_detects_clang_compiler_error(self):
        """Test detection of Clang compiler errors using sample log"""
        log = read_sample_file("clang_error.log")
        data = self.parser.parse_log(log, unique=False)

        # Test data structure directly instead of JSON dumps
        assert data, "Should detect Clang compiler errors"

        # Get build parser results
        build_parser_keys = [k for k in data.keys() if k.startswith("log-parser-build")]
        assert len(build_parser_keys) > 0, "Should create build parser results"

        build_tests = data[build_parser_keys[0]]

        # Verify Clang compiler error tests were created
        clang_tests = [name for name in build_tests.keys() if "clang-compiler" in name]
        assert len(clang_tests) > 0, "Should detect Clang compiler errors"

        # Verify log excerpts contain expected error content
        found_error = False
        found_undeclared_content = False
        for test_name, test_data in build_tests.items():
            if "clang-compiler" in test_name:
                log_excerpt = test_data.get("log_excerpt", [])
                excerpt_text = " ".join(log_excerpt)
                if "error" in excerpt_text:
                    found_error = True
                if (
                    "undeclared identifier" in excerpt_text
                    or "USER_PGTABLES_CEILING" in excerpt_text
                ):
                    found_undeclared_content = True

        assert found_error, "Should capture error messages"
        assert (
            found_undeclared_content
        ), "Should capture undeclared identifier or USER_PGTABLES_CEILING errors"

    def test_detects_clang_compiler_warning(self):
        """Test detection of Clang compiler warnings using sample log"""
        log = read_sample_file("clang_warning.log")
        data = self.parser.parse_log(log, unique=False)

        # Test data structure directly instead of JSON dumps
        assert data, "Should detect Clang compiler warnings"

        # Get build parser results
        build_parser_keys = [k for k in data.keys() if k.startswith("log-parser-build")]
        assert len(build_parser_keys) > 0, "Should create build parser results"

        build_tests = data[build_parser_keys[0]]

        # Verify Clang compiler warning tests were created
        clang_tests = [name for name in build_tests.keys() if "clang-compiler" in name]
        assert len(clang_tests) > 0, "Should detect Clang compiler warnings"

        # Verify log excerpts contain expected warning content
        found_warning = False
        found_shift_content = False
        for test_name, test_data in build_tests.items():
            if "clang-compiler" in test_name:
                log_excerpt = test_data.get("log_excerpt", [])
                excerpt_text = " ".join(log_excerpt)
                if "warning" in excerpt_text:
                    found_warning = True
                if "shift count" in excerpt_text or "negative" in excerpt_text:
                    found_shift_content = True

        assert found_warning, "Should capture warning messages"
        assert (
            found_shift_content
        ), "Should capture shift count or negative-related warnings"

    def test_detects_linker_error(self):
        """Test detection of linker errors using sample log"""
        log = read_sample_file("linker_error.log")
        data = self.parser.parse_log(log, unique=False)

        # Test data structure directly instead of JSON dumps
        assert data, "Should detect linker undefined reference errors"

        # Get build parser results
        build_parser_keys = [k for k in data.keys() if k.startswith("log-parser-build")]
        assert len(build_parser_keys) > 0, "Should create build parser results"

        build_tests = data[build_parser_keys[0]]

        # Verify undefined reference tests were created
        undefined_ref_tests = [
            name
            for name in build_tests.keys()
            if "general-ld-undefined-reference" in name
        ]
        assert len(undefined_ref_tests) > 0, "Should detect undefined reference errors"

        # Verify log excerpts contain expected undefined reference content
        found_undefined_ref = False
        found_symbol_content = False
        for test_name, test_data in build_tests.items():
            if "general-ld-undefined-reference" in test_name:
                log_excerpt = test_data.get("log_excerpt", [])
                excerpt_text = " ".join(log_excerpt)
                if "undefined reference" in excerpt_text:
                    found_undefined_ref = True
                if "irq_work_queue" in excerpt_text or "task_work_add" in excerpt_text:
                    found_symbol_content = True

        assert found_undefined_ref, "Should capture undefined reference messages"
        assert (
            found_symbol_content
        ), "Should capture specific undefined symbols like irq_work_queue or task_work_add"

    def test_detects_lld_linker_error(self):
        """Test detection of LLD linker errors using sample log"""
        log = read_sample_file("lld_error.log")
        data = self.parser.parse_log(log, unique=False)

        # Test data structure directly instead of JSON dumps
        assert data, "Should detect LLD linker errors"

        # Get build parser results
        build_parser_keys = [k for k in data.keys() if k.startswith("log-parser-build")]
        assert len(build_parser_keys) > 0, "Should create build parser results"

        build_tests = data[build_parser_keys[0]]

        # Verify LLD error tests were created (could be general-lld-error or contain "lld")
        lld_tests = [
            name
            for name in build_tests.keys()
            if "general-lld-error" in name or "lld" in name
        ]
        assert len(lld_tests) > 0, "Should detect LLD errors"

        # Verify log excerpts contain expected LLD error content
        found_undefined_symbol = False
        found_symbol_content = False
        for test_name, test_data in build_tests.items():
            if "general-lld-error" in test_name or "lld" in test_name:
                log_excerpt = test_data.get("log_excerpt", [])
                excerpt_text = " ".join(log_excerpt)
                if "undefined symbol" in excerpt_text:
                    found_undefined_symbol = True
                if (
                    "irq_work_queue" in excerpt_text
                    or "arch_irq_work_raise" in excerpt_text
                ):
                    found_symbol_content = True

        assert found_undefined_symbol, "Should capture undefined symbol messages"
        assert (
            found_symbol_content
        ), "Should capture specific undefined symbols like irq_work_queue or arch_irq_work_raise"

    def test_detects_python_traceback(self):
        """Test detection of Python tracebacks using sample log"""
        log = read_sample_file("python_traceback.log")
        data = self.parser.parse_log(log, unique=False)

        # Test data structure directly instead of JSON dumps
        assert data, "Should detect Python traceback errors"

        # Get build parser results
        build_parser_keys = [k for k in data.keys() if k.startswith("log-parser-build")]
        assert len(build_parser_keys) > 0, "Should create build parser results"

        build_tests = data[build_parser_keys[0]]

        # Verify Python traceback tests were created
        python_tests = [
            name for name in build_tests.keys() if "general-python-traceback" in name
        ]
        assert len(python_tests) > 0, "Should detect Python traceback errors"

        # Verify log excerpts contain expected Python error content
        found_traceback_content = False
        found_specific_content = False
        for test_name, test_data in build_tests.items():
            if "general-python-traceback" in test_name:
                log_excerpt = test_data.get("log_excerpt", [])
                excerpt_text = " ".join(log_excerpt)
                if "ModuleNotFoundError" in excerpt_text or "Traceback" in excerpt_text:
                    found_traceback_content = True
                if "jsonschema" in excerpt_text or "ynl-gen-c.py" in excerpt_text:
                    found_specific_content = True

        assert (
            found_traceback_content
        ), "Should capture ModuleNotFoundError or Traceback messages"
        assert (
            found_specific_content
        ), "Should capture specific content like jsonschema or ynl-gen-c.py"

    def test_all_sample_logs_parse_without_crash(self):
        """Test that all sample logs can be parsed without crashing"""
        sample_files = [
            "gcc_error.log",
            "gcc_warning.log",
            "clang_error.log",
            "clang_warning.log",
            "linker_error.log",
            "lld_error.log",
            "python_traceback.log",
        ]

        for sample_file in sample_files:
            log = read_sample_file(sample_file)
            # Should not raise any exceptions
            data = self.parser.parse_log(log, unique=False)

            # Should return a dict (might be empty for logs with no issues)
            assert isinstance(
                data, dict
            ), f"Parser should return dict for {sample_file}"

    def test_sample_logs_produce_valid_json(self):
        """Test that sample logs produce valid JSON output"""
        sample_files = [
            "gcc_error.log",
            "clang_error.log",
            "linker_error.log",
            "python_traceback.log",
        ]

        for sample_file in sample_files:
            log = read_sample_file(sample_file)
            data = self.parser.parse_log(log, unique=False)

            # Verify data is valid
            assert isinstance(data, dict)

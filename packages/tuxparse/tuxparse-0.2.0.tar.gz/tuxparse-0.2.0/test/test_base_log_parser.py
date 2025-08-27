import re
from collections import defaultdict

from tuxparse.lib.base_log_parser import BaseLogParser


class TestBaseLogParser:
    """Tests for base_log_parser functionality"""

    def setup_method(self):
        self.parser = BaseLogParser()
        self.snippet = "[    0.123] Kernel panic - not syncing: Attempted to kill init 64! exitcode=0x00000009"

    def test_remove_numbers_and_time(self):
        """Test removing numbers and time from log snippet"""
        result = self.parser.remove_numbers_and_time(self.snippet)
        expected = " Kernel panic - not syncing: Attempted to kill init ! exitcode="
        assert result == expected

    def test_remove_numbers_and_time_with_pid(self):
        """Test removing numbers and time with PID in log"""
        snippet1 = "<3>[    2.491276][    T1] BUG: KCSAN: data-race in console_emit_next_record / console_trylock_spinning"
        result = self.parser.remove_numbers_and_time(snippet1)
        expected = " BUG: KCSAN: data-race in console_emit_next_record / console_trylock_spinning"
        assert result == expected

        snippet2 = "<3>[  157.430085][    C1] BUG: KCSAN: data-race in ktime_get / timekeeping_advance"
        result = self.parser.remove_numbers_and_time(snippet2)
        expected = " BUG: KCSAN: data-race in ktime_get / timekeeping_advance"
        assert result == expected

    def test_create_name_no_regex(self):
        """Test create_name when no regex is provided"""
        name = self.parser.create_name(self.snippet)
        assert name is None

    def test_create_name_with_regex_match(self):
        """Test create_name when regex matches"""
        regex = re.compile(r"panic.*", re.S | re.M)
        name = self.parser.create_name(self.snippet, regex)
        assert name == "panic__not_syncing_Attempted_to_kill_init_exitcode"

    def test_create_name_with_regex_no_match(self):
        """Test create_name when regex doesn't match"""
        regex = re.compile(r"oops.*", re.S | re.M)
        name = self.parser.create_name(self.snippet, regex)
        assert name is None

    def test_create_shasum(self):
        """Test SHA sum creation is consistent"""
        sha_sum = self.parser.create_shasum(self.snippet)
        expected = "1e8e593d"
        assert sha_sum == expected

    def test_create_name_log_dict_exclude_numbers(self):
        """Test creating the dict containing the "name" and "log lines" pairs -
        case where we want to exclude the numbers before doing the SHA"""
        (
            tests_without_shas_to_create,
            tests_with_shas_to_create,
        ) = self.parser.create_name_log_dict(
            "test_name", ["log lines 1", "log lines 2"]
        )
        expected_tests_without_shas_to_create = defaultdict(
            list, {"test_name": ["log lines 1", "log lines 2"]}
        )
        expected_tests_with_shas_to_create = defaultdict(
            list,
            {
                "test_name-1677bef2": [
                    "log lines 1",
                    "log lines 2",
                ]
            },
        )

        assert dict(tests_without_shas_to_create) == dict(
            expected_tests_without_shas_to_create
        )
        assert dict(tests_with_shas_to_create) == dict(
            expected_tests_with_shas_to_create
        )

    def test_create_name_log_dict_keep_numbers(self):
        """Test creating the dict containing the "name" and "log lines" pairs -
        case where we want to keep the numbers before doing the SHA"""
        (
            tests_without_shas_to_create,
            tests_with_shas_to_create,
        ) = self.parser.create_name_log_dict("test_name", ["log lines1", "log lines2"])
        expected_tests_without_shas_to_create = defaultdict(
            list, {"test_name": ["log lines1", "log lines2"]}
        )
        expected_tests_with_shas_to_create = defaultdict(
            list,
            {
                "test_name-8166dde0": [
                    "log lines1",
                ],
                "test_name-335a19ed": [
                    "log lines2",
                ],
            },
        )

        assert dict(tests_without_shas_to_create) == dict(
            expected_tests_without_shas_to_create
        )
        assert dict(tests_with_shas_to_create) == dict(
            expected_tests_with_shas_to_create
        )

    def test_create_name_log_dict_no_shas(self):
        """Test creating the dict containing the "name" and "log lines" pairs"""
        (
            tests_without_shas_to_create,
            tests_with_shas_to_create,
        ) = self.parser.create_name_log_dict(
            "test_name", ["log lines1", "log lines2"], create_shas=False
        )
        expected_tests_without_shas_to_create = defaultdict(
            list, {"test_name": ["log lines1", "log lines2"]}
        )
        expected_tests_with_shas_to_create = None

        assert dict(tests_without_shas_to_create) == dict(
            expected_tests_without_shas_to_create
        )
        assert tests_with_shas_to_create == expected_tests_with_shas_to_create

    def test_create_tests(self):
        """Test the wrapper for extracting the regexes then creating the tests"""
        (
            tests_without_shas_to_create,
            tests_with_shas_to_create,
        ) = self.parser.create_tests(
            "suite_name", "test_name", {"log lines 1", "log lines 2"}
        )

        # Should create proper test dictionaries
        assert "test_name" in tests_without_shas_to_create
        assert len(tests_with_shas_to_create) > 0

        # Check that SHA-based test names are created
        sha_test_names = list(tests_with_shas_to_create.keys())
        assert any("test_name-" in name for name in sha_test_names)

    def test_compile_regexes_single(self):
        """Test compiling a single regex"""
        regexes = [
            (
                "check-kernel-panic",
                r"Kernel panic - not syncing.*?$",
                r"Kernel [^\+\n]*",
            )
        ]

        compiled_regex = self.parser.compile_regexes(regexes)
        log = """[    0.123] Kernel panic - not syncing: Attempted to kill init 64! exitcode=0x00000009
[    0.999] Kernel panic - not syncing: Attempted to kill init! exitcode=0x00000008"""
        matches = compiled_regex.findall(log)

        snippets = self.parser.join_matches(matches, regexes)

        assert (
            "Kernel panic - not syncing: Attempted to kill init 64! exitcode=0x00000009"
            in snippets[0]
        )
        assert (
            "Kernel panic - not syncing: Attempted to kill init! exitcode=0x00000008"
            in snippets[0]
        )
        assert len(matches) == 2

    def test_compile_regexes_multiple(self):
        """Test compiling multiple regexes"""
        regexes = [
            (
                "check-kernel-panic",
                r"Kernel panic - not syncing.*?$",
                r"Kernel [^\+\n]*",
            ),
            ("check-kernel-oops", r"^[^\n]+Oops(?: -|:).*?$", r"Oops[^\+\n]*"),
        ]
        compiled_regex = self.parser.compile_regexes(regexes)

        log = """[    0.123] Kernel panic - not syncing: Attempted to kill init 64! exitcode=0x00000009
[    0.999] Kernel panic - not syncing: Attempted to kill init! exitcode=0x00000008
[   14.461360] Internal error: Oops - BUG: 0 [#0] PREEMPT SMP"""
        matches = compiled_regex.findall(log)

        snippets = self.parser.join_matches(matches, regexes)

        assert (
            "Kernel panic - not syncing: Attempted to kill init 64! exitcode=0x00000009"
            in snippets[0]
        )
        assert (
            "Kernel panic - not syncing: Attempted to kill init! exitcode=0x00000008"
            in snippets[0]
        )
        assert (
            "[   14.461360] Internal error: Oops - BUG: 0 [#0] PREEMPT SMP"
            in snippets[1]
        )

        assert (
            len(snippets) == 2
        )  # There are 2 regexes being tested so there is a dict entry for each regex
        assert len(snippets[0]) == 2  # Regex ID 0 has 2 matches
        assert len(snippets[1]) == 1  # Regex ID 1 has 1 match

    def test_join_matches(self):
        """Test joining regex matches into proper format"""
        matches = [
            (
                "Kernel panic - not syncing: Attempted to kill init 64! exitcode=0x00000009",
                "",
            ),
            (
                "Kernel panic - not syncing: Attempted to kill init! exitcode=0x00000008",
                "",
            ),
            ("", "[   14.461360] Internal error: Oops - BUG: 0 [#0] PREEMPT SMP"),
        ]
        regexes = [
            (
                "check-kernel-panic",
                r"Kernel panic - not syncing.*?$",
                r"Kernel [^\+\n]*",
            ),
            ("check-kernel-oops", r"^[^\n]+Oops(?: -|:).*?$", r"Oops[^\+\n]*"),
        ]
        snippets = self.parser.join_matches(matches, regexes)
        expected_snippets = {
            0: [
                "Kernel panic - not syncing: Attempted to kill init 64! exitcode=0x00000009",
                "Kernel panic - not syncing: Attempted to kill init! exitcode=0x00000008",
            ],
            1: ["[   14.461360] Internal error: Oops - BUG: 0 [#0] PREEMPT SMP"],
        }

        assert snippets == expected_snippets

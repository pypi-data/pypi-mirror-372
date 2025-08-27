#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: set ts=4
#
# Copyright 2025-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import hashlib
import logging
import re
from collections import defaultdict

REGEX_NAME = 0
REGEX_BODY = 1
REGEX_EXTRACT_NAME = 2

tstamp = r"(?:\[[ \d]+\.[ \d]+\]|<\d+>)"
pid = r"(?:\s*?\[\s*?[CT]\d+\s*?\])"
not_newline_or_plus = r"[^\+\n]"
square_brackets_and_contents = r"\[[^\]]+\]"


def slugify(line):
    non_ascii_pattern = r"[^A-Za-z0-9_-]+"
    line = re.sub(r"\[\d{1,5}\]", "", line)
    return re.sub(
        r"_-", "_", re.sub(r"(^_|_$)", "", re.sub(non_ascii_pattern, "_", line))
    )


class BaseLogParser:
    def compile_regexes(self, regexes):
        with_brackets = [r"(%s)" % r[REGEX_BODY] for r in regexes]
        combined = r"|".join(with_brackets)

        # In the case where there is only one regex, we need to add extra
        # bracket around it for it to behave the same as the multiple regex
        # case
        if len(regexes) == 1:
            combined = f"({combined})"

        return re.compile(combined, re.S | re.M)

    def remove_numbers_and_time(self, snippet):
        # allocated by task 285 on cpu 0 at 38.982743s (0.007174s ago):
        # Removes [digit(s)].[digit(s)]s
        cleaned_seconds = re.sub(r"\b\d+\.\d+s\b", "", snippet)
        # [   92.236941] CPU: 1 PID: 191 Comm: kunit_try_catch Tainted: G        W         5.15.75-rc1 #1
        # <4>[   87.925462] CPU: 0 PID: 135 Comm: (crub_all) Not tainted 6.7.0-next-20240111 #14
        # Remove '(Not t|T)ainted', to the end of the line.
        without_tainted = re.sub(r"(Not t|T)ainted.*", "", cleaned_seconds)

        # x23: ffff9b7275bc6f90 x22: ffff9b7275bcfb50 x21: fff00000cc80ef88
        # x20: 1ffff00010668fb8 x19: ffff8000800879f0 x18: 00000000805c0b5c
        # Remove words with hex numbers.
        # <3>[    2.491276][    T1] BUG: KCSAN: data-race in console_emit_next_record / console_trylock_spinning
        # -> <>[    .][    T1] BUG: KCSAN: data-race in console_emit_next_record / console_trylock_spinning
        without_hex = re.sub(r"\b(?:0x)?[a-fA-F0-9]+\b", "", without_tainted)

        # <>[ 1067.461794][  T132] BUG: KCSAN: data-race in do_page_fault spectre_v4_enable_task_mitigation
        # -> <>[ .][  T132] BUG: KCSAN: data-race in do_page_fault spectre_v_enable_task_mitigation
        # But should not remove numbers from functions.
        without_numbers = re.sub(
            r"(0x[a-f0-9]+|[<\[][0-9a-f]+?[>\]]|\b\d+\b(?!\s*\())", "", without_hex
        )

        # <>[ .][  T132] BUG: KCSAN: data-race in do_page_fault spectre_v_enable_task_mitigation
        # ->  BUG: KCSAN: data-race in do_page_fault spectre_v_enable_task_mitigation
        without_time = re.sub(
            f"^<?>?{square_brackets_and_contents}({square_brackets_and_contents})?",
            "",
            without_numbers,
        )  # noqa

        return without_time

    def create_name(self, snippet, compiled_regex=None):
        matches = None
        if compiled_regex:
            matches = compiled_regex.findall(snippet)
        if not matches:
            # Only extract a name if we provide a regex to extract the name and
            # there is a match
            return None
        snippet = matches[0]
        without_numbers_and_time = self.remove_numbers_and_time(snippet)

        return slugify(without_numbers_and_time)

    def create_shasum(self, snippet):
        sha = hashlib.sha256()
        without_numbers_and_time = self.remove_numbers_and_time(snippet)
        sha.update(without_numbers_and_time.encode())
        return sha.hexdigest()[:8]

    def create_name_log_dict(self, test_name, lines, test_regex=None, create_shas=True):
        """
        Produce a dictionary with the test names as keys and the extracted logs
        for that test name as values. There will be at least one test name per
        regex. If there were any matches for a given regex, then a new test
        will be generated using test_name + shasum.
        """
        # Run the REGEX_EXTRACT_NAME regex over the log lines to sort them by
        # extracted name. If no name is extracted or the log parser did not
        # have any output for a particular regex, just use the default name
        # (for example "check-kernel-oops").
        tests_without_shas_to_create = defaultdict(list)
        tests_with_shas_to_create = None

        # Memory protection: limit number of tests to prevent endless loop scenarios
        max_tests_per_extracted_name = (
            30  # Reasonable limit per unique extracted pattern
        )
        extracted_name_counts = {}  # Track count per unique extracted name
        warned_patterns = set()  # Track which patterns we've already warned about

        # If there are lines, then create the tests for these.
        for line in lines:
            extracted_name = self.create_name(line, test_regex)
            if extracted_name:
                max_name_length = 256
                # If adding SHAs, limit the name length to 247 characters,
                # since the max name length for SuiteMetadata in SQUAD is 256
                # characters. The SHA and "-" take 11 characters: 256-9=247
                if create_shas:
                    max_name_length -= 9
                extended_test_name = f"{test_name}-{extracted_name}"[:max_name_length]
            else:
                extended_test_name = test_name
                extracted_name = test_name  # Use test_name as the key for counting

            # Check limit per unique extracted name pattern
            current_count = extracted_name_counts.get(extracted_name, 0)
            if current_count >= max_tests_per_extracted_name:
                # Log warning for this specific pattern but continue with other patterns
                if extracted_name not in warned_patterns:
                    logger = logging.getLogger()
                    logger.warning(
                        f"Truncated test creation at {max_tests_per_extracted_name} tests for pattern '{extracted_name}' in regex '{test_name}' to prevent memory exhaustion from repetitive patterns"
                    )
                    warned_patterns.add(extracted_name)
                continue  # Skip this line but continue processing other patterns

            # Maintain order while avoiding duplicates
            if line not in tests_without_shas_to_create[extended_test_name]:
                tests_without_shas_to_create[extended_test_name].append(line)
                extracted_name_counts[extracted_name] = current_count + 1

        if create_shas:
            tests_with_shas_to_create = defaultdict(list)
            for name, test_lines in tests_without_shas_to_create.items():
                # Some lines of the matched regex might be the same, and we don't want to create
                # multiple tests like test1-sha1, test1-sha1, etc, so we'll create a set of sha1sums
                # then create only new tests for unique sha's

                for line in test_lines:
                    sha = self.create_shasum(line)
                    name_with_sha = f"{name}-{sha}"
                    # Maintain order while avoiding duplicates
                    if line not in tests_with_shas_to_create[name_with_sha]:
                        tests_with_shas_to_create[name_with_sha].append(line)

        return tests_without_shas_to_create, tests_with_shas_to_create

    def create_tests(
        self,
        suite_name,
        test_name,
        lines,
        test_regex=None,
        create_shas=True,
    ):
        """
        There will be at least one test per regex. If there were any match for
        a given regex, then a new test will be generated using test_name +
        shasum. This helps comparing kernel logs across different builds
        """

        (
            tests_without_shas_to_create,
            tests_with_shas_to_create,
        ) = self.create_name_log_dict(
            test_name, lines, test_regex, create_shas=create_shas
        )
        return tests_without_shas_to_create, tests_with_shas_to_create

    def join_matches(self, matches, regexes):
        """
        group regex in python are returned as a list of tuples which each
        group match in one of the positions in the tuple. Example:
        regex = r'(a)|(b)|(c)'
        matches = [
            ('match a', '', ''),
            ('', 'match b', ''),
            ('match a', '', ''),
            ('', '', 'match c')
        ]
        """
        snippets = {regex_id: [] for regex_id in range(len(regexes))}
        for match in matches:
            for regex_id in range(len(regexes)):
                if len(match[regex_id]) > 0:
                    snippets[regex_id].append(match[regex_id])
        return snippets

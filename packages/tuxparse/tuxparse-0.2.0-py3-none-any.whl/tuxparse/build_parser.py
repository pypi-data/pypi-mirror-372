#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: set ts=4
#
# Copyright 2025-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import logging
import re
from collections import defaultdict

from tuxparse.lib.base_log_parser import (
    REGEX_EXTRACT_NAME,
    REGEX_NAME,
    BaseLogParser,
    slugify,
)

logger = logging.getLogger()

file_path = r"^(?:[^\n]*?:(?:\d+:){2}|<[^\n]*?>:)"
gcc_clang_compiler_error_warning = rf"{file_path} (?:error|warning): [^\n]+\n(?:^[ \t]+[^\n]+\n|^{file_path} note:[^\n]+\n)*"

MULTILINERS_GCC = [
    (
        "gcc-compiler",
        gcc_clang_compiler_error_warning,
        r"^[^\n]*(?:error|warning)[^\n]*$",
    ),
]

ONELINERS_GCC: list[str] = []


MULTILINERS_CLANG = [
    (
        "clang-compiler",
        gcc_clang_compiler_error_warning,
        r"^[^\n]*(?:error|warning)[^\n]*$",
    ),
]

ONELINERS_CLANG = [
    (
        "clang-compiler-single-line",
        "^clang: (?:error|warning).*?$",
        r"^[^\n]*(?:error|warning).*?$",
    ),
    (
        "clang-compiler-fatal-error",
        "^fatal error.*?$",
        r"^fatal error.*?$",
    ),
]

MULTILINERS_GENERAL = [
    (
        "general-not-a-git-repo",
        r"^[^\n]*fatal: not a git repository.*?not set\)\.$",
        r"fatal: not a git repository.*?$",
    ),
    (
        "general-unexpected-argument",
        r"^[^\n]*error: Found argument.*?--help$",
        r"error: Found argument.*?$",
    ),
    (
        "general-broken-32-bit",
        r"^[^\n]*Warning: you seem to have a broken 32-bit build.*?(?:If[^\n]*?try:(?:\n|\s+.+?$)+)+",
        r"Warning:.*?$",
    ),
    (
        "general-makefile-overriding",
        r"^[^\n]*warning: overriding recipe for target.*?ignoring old recipe for target.*?$",
        r"^[^\n]*warning:.*?$",
    ),
    (
        "general-unmet-dependencies",
        r"^WARNING: unmet direct dependencies detected for.*?$(?:\n +[^\n]+)*",
        r"^WARNING: unmet direct dependencies detected for.*?$",
    ),
    (
        "general-ldd",
        r"^[^\n]*?lld:[^\n]+?(?:warning|error):.*?$(?:\n^>>>[^\n]+)*",
        r"lld:.*?$",
    ),
    (
        "general-ld",
        r"^[^\n]*?ld:[^\n]+?(?:warning|error):[^\n]*?$(?:\n^[^\n]*?NOTE:[^\n]+)*",
        r"(?:warning|error):.*?$",
    ),
    (
        "general-objcopy",
        r"^[^\n]*?objcopy:[^\n]+?(?:warning|error):[^\n]*?$(?:\n^[^\n]*?NOTE:[^\n]+)*",
        r"(?:warning|error):.*?$",
    ),
    (
        "general-ld-undefined-reference",
        r"^[^\n]*?ld[^\n]*?$\n^[^\n]+undefined reference.*?$",
        r"undefined reference.*?$",
    ),
    (
        "general-modpost",
        r"^[^\n]*?ERROR: modpost:[^\n]*?$(?:\n^To see.*?:$\n^.*?$)?",
        r"ERROR.*?$",
    ),
    (
        "general-modpost",
        r"^[^\n]*?WARNING: modpost:[^\n]*?$(?:\n^To see.*?:$\n^.*?$)?",
        r"WARNING.*?$",
    ),
    (
        "general-python-traceback",
        r"Traceback.*?^[^\s]+Error: .*?$",
        r"^[^\s]+Error: .*?$",
    ),
]

ONELINERS_GENERAL = [
    (
        "general-no-such-file-or-directory",
        r"^[^\n]+?No such file or directory.*?$",
        r"^[^\n]+?No such file or directory.*?$",
    ),
    (
        "general-no-targets",
        r"^[^\n]+?No targets.*?$",
        r"^[^\n]+?No targets.*?$",
    ),
    (
        "general-no-rule-to-make-target",
        r"^[^\n]+?No rule to make target.*?$",
        r"^[^\n]+?No rule to make target",
    ),
    (
        "general-makefile-config",
        r"^Makefile.config:\d+:.*?$",
        r"^Makefile.config:\d+:.*?$",
    ),
    (
        "general-not-found",
        r"^[^\n]*?not found.*?$",
        r"^[^\n]*?not found.*?$",
    ),
    (
        "general-kernel-abi",
        r"^Warning: Kernel ABI header at.*?$",
        r"Warning: Kernel ABI header at.*?$",
    ),
    (
        "general-missing",
        r"^Warning: missing.*?$",
        r"Warning: missing.*?$",
    ),
    (
        "general-dtc",
        r"^[^\n]*?Warning \([^\n]*?\).*?$",
        r"Warning.*?$",
    ),
    (
        "general-register-allocation",
        r"^[^\n]*?error: register allocation failed.*?$",
        r"error.*?$",
    ),
    (
        "general-uppercase-error",
        r"^ERROR:.*?$",
        r"^ERROR:.*?$",
    ),
]

# Tip: broader regexes should come first
REGEXES_GCC = MULTILINERS_GCC + MULTILINERS_GENERAL + ONELINERS_GCC + ONELINERS_GENERAL
REGEXES_CLANG = (
    MULTILINERS_CLANG + MULTILINERS_GENERAL + ONELINERS_CLANG + ONELINERS_GENERAL
)

supported_toolchains = {
    "gcc": REGEXES_GCC,
    "clang": REGEXES_CLANG,
}

make_regex = r"^make .*?$"
in_file_regex = r"^In file[^\n]*[:,]$(?:\n^(?:\s+|In file)[^\n]*[:,]$)*"
in_function_regex = r"^[^\n]*?In function.*?:$"
entering_dir_regex = r"^make\[(?:\d+)\]: Entering directory.*?$"
leaving_dir_regex = r"^make\[(?:\d+)\]: Leaving directory.*?$"

split_regex_gcc = rf"(.*?)({make_regex}|{in_file_regex}|{in_function_regex}|{entering_dir_regex}|{leaving_dir_regex})"


class BuildParser(BaseLogParser):
    def test_name(self, text):
        # Remove "builds/linux" if there
        text = re.sub(r"builds/linux", "", text)

        # Change "/" and "." to "_" for readability
        text = re.sub(r"[/\.]", "_", text)

        # Remove numbers and hex
        text = re.sub(r"(0x[a-f0-9]+|[<\[][0-9a-f]+?[>\]]|\d+)", "", text)

        # Remove "{...}" and "[...]"
        text = re.sub(r"\{.+?\}", "", text)
        text = re.sub(r"\[.+?\]", "", text)

        return text

    def create_name(self, snippet, compiled_regex=None):
        matches = None
        if compiled_regex:
            matches = compiled_regex.findall(snippet)
        if not matches:
            # Only extract a name if we provide a regex to extract the name and
            # there is a match
            return None
        snippet = matches[0]
        without_numbers = re.sub(
            r"(0x[a-f0-9]+|[<\[][0-9a-f]+?[>\]]|\b\d+\b(?!\s*\())", "", snippet
        )

        # Remove tmp .o files
        without_tmp = re.sub(r"\/tmp\S*?\/\S*?\.o", "", without_numbers)

        # Remove .o files in ()
        without_o_in_brackets = re.sub(r"\(\S*?\.o\)", "", without_tmp)

        name = slugify(self.test_name(without_o_in_brackets))

        return name

    def post_process_test_name(self, text):
        """Post-process test name by cleaning up path and special characters"""
        # This method provides compatibility with SQUAD test expectations
        return self.test_name(text)

    def split_by_regex(self, log, regex):
        # Split up the log by the keywords we want to capture
        s_lines_compiled = re.compile(regex, re.DOTALL | re.MULTILINE)
        split_by_regex_list = s_lines_compiled.split(log)
        split_by_regex_list = [
            f for f in split_by_regex_list if f is not None and f != ""
        ]

        return split_by_regex_list

    def process_blocks(
        self,
        blocks_to_process,
        regexes,
        make_regex=make_regex,
        entering_dir_regex=entering_dir_regex,
        leaving_dir_regex=leaving_dir_regex,
        in_file_regex=in_file_regex,
        in_function_regex=in_function_regex,
    ):
        snippets = dict()
        regex_compiled = self.compile_regexes(regexes)
        make_regex_compiled = re.compile(make_regex, re.DOTALL | re.MULTILINE)
        entering_dir_regex_compiled = re.compile(
            entering_dir_regex, re.DOTALL | re.MULTILINE
        )
        leaving_dir_regex_compiled = re.compile(
            leaving_dir_regex, re.DOTALL | re.MULTILINE
        )
        in_file_regex_compiled = re.compile(in_file_regex, re.DOTALL | re.MULTILINE)
        in_function_regex_compiled = re.compile(
            in_function_regex, re.DOTALL | re.MULTILINE
        )

        # For tracking the last piece of information we saw
        make_command = None
        entering_dir = None
        in_file = None
        in_function = None

        for regex_id in range(len(regexes)):
            snippets[regex_id] = []
        for block in blocks_to_process:
            if make_regex_compiled.match(block):
                make_command = block
                entering_dir = None
                in_file = None
                in_function = None
            elif entering_dir_regex_compiled.match(block):
                entering_dir = block
                in_file = None
                in_function = None
            elif leaving_dir_regex_compiled.match(block):
                entering_dir = None
                in_file = None
                in_function = None
            elif in_file_regex_compiled.match(block):
                in_file = block
                in_function = None
            elif in_function_regex_compiled.match(block):
                in_function = block
            else:
                matches = regex_compiled.findall(block)
                sub_snippets = self.join_matches(matches, regexes)
                prepend = ""
                if make_command:
                    prepend += make_command + "\n"
                if entering_dir:
                    prepend += entering_dir + "\n"
                if in_file:
                    prepend += in_file + "\n"
                if in_function:
                    prepend += in_function + "\n"
                for regex_id in range(len(regexes)):
                    for s in sub_snippets[regex_id]:
                        snippets[regex_id].append(prepend + s)

        return snippets

    def split_log_by_make(self, log):
        """Splits log into chunks starting with 'make --silent' lines only"""
        chunks = []
        current_cmd = None
        current_lines = []
        for line in log.splitlines():
            if re.match(r"^make --silent(?:\s|$)", line):
                if current_cmd and current_lines:
                    chunks.append((current_cmd, "\n".join(current_lines)))
                    current_lines = []
                current_cmd = line
            if current_cmd:
                current_lines.append(line)
        if current_cmd and current_lines:
            chunks.append((current_cmd, "\n".join(current_lines)))
        return chunks

    def clean_suite_postfix(self, make_cmd):
        """Extract a clean postfix for suite name from a 'make --silent ...' command"""
        if not make_cmd.startswith("make --silent"):
            return None  # Only handle make --silent commands

        # Remove:
        #   --flags
        #   KEY=value
        make_cmd = re.sub(r"--\S+\s*", "", make_cmd)
        make_cmd = re.sub(r"\b[A-Z_]+=\/?\S+\s*", "", make_cmd)
        make_cmd = re.sub(r"'[^']+'\s*", "", make_cmd)

        parts = make_cmd.strip().split()
        targets = [p for p in parts if p != "make"]

        return "_".join(targets) if targets else "kernel"

    def _extract_error_signature(self, error_line):
        """Extract the core error message for deduplication"""
        lines = error_line.split("\n")
        for line in lines:
            # Find the actual error/warning line
            if any(
                marker in line for marker in ["error:", "warning:", "No rule to make"]
            ):
                # Remove line numbers, addresses, and file-specific paths for comparison
                signature = re.sub(r":\d+:\d+:", ":XX:XX:", line)
                signature = re.sub(r"/[^\s]+/", "/PATH/", signature)
                signature = re.sub(r"\b\d+\b", "NUM", signature)
                return signature.strip()
        return error_line.strip()

    def _extract_affected_files(self, error_line):
        """Extract file information from error line"""
        files = []
        lines = error_line.split("\n")
        for line in lines:
            # Extract file:line from error line
            match = re.search(r"^([^:]+):(\d+):(\d+):", line)
            if match:
                files.append(f"{match.group(1)}:{match.group(2)}")
        return files

    def parse_log(self, log_input, unique):
        """
        Check:
            - There is a log file
            - If running as SQUAD plugin, the testrun contains the "build"
              suite - this tells us that the testrun's log is a build log
        """
        if log_input is None:
            return {}

        # Handle both string and file object inputs
        if isinstance(log_input, str):
            log_file = log_input
        else:
            # File object input - read content
            log_file = log_input.read()

        if not log_file:
            return {}

        regexes = None
        for toolchain, toolchain_regexes in supported_toolchains.items():
            if f"--toolchain={toolchain}" in log_file:
                toolchain_name = toolchain
                regexes = toolchain_regexes

        # If a supported toolchain was not found in the log
        if regexes is None:
            return {}

        # If running in SQUAD, create the suite
        suite_name = f"log-parser-build-{toolchain_name}"

        snippets = defaultdict(list)

        # Compile regexes once for performance
        regex_compiled = self.compile_regexes(regexes)

        for make_cmd, snippet in self.split_log_by_make(log_file):
            # Use direct regex matching instead of complex split_by_regex approach
            matches = regex_compiled.findall(snippet)
            sub_snippets = self.join_matches(matches, regexes)

            has_issues = any(sub_snippets[regex_id] for regex_id in range(len(regexes)))
            if not has_issues:
                continue  # Skip clean chunks

            postfix = self.clean_suite_postfix(make_cmd)
            suite_name = f"log-parser-build-{postfix}"

            for regex_id in range(len(regexes)):
                snippets[(suite_name, regex_id)] += sub_snippets[regex_id]

        results = defaultdict(
            lambda: defaultdict(lambda: {"log_excerpt": "", "result": "fail"})
        )
        for (suite_name, regex_id), blocks in snippets.items():
            test_name = regexes[regex_id][REGEX_NAME]
            regex_pattern = regexes[regex_id][REGEX_EXTRACT_NAME]
            test_name_regex = None
            if regex_pattern:
                test_name_regex = re.compile(regex_pattern, re.S | re.M)
            tests_without_shas_to_create, _ = self.create_tests(
                suite_name,
                test_name,
                blocks,
                test_name_regex,
                create_shas=False,
            )
            # Deduplicate errors by signature while preserving file context
            error_signatures = {}  # signature -> {excerpt, affected_files, test_name}

            for name, lines in tests_without_shas_to_create.items():
                for line in lines:
                    signature = self._extract_error_signature(line)
                    affected_files = self._extract_affected_files(line)

                    if signature not in error_signatures:
                        error_signatures[signature] = {
                            "excerpt": line,
                            "affected_files": set(affected_files),
                            "test_name": name,
                        }
                    else:
                        # Add files to existing signature
                        error_signatures[signature]["affected_files"].update(
                            affected_files
                        )

            # Create deduplicated results
            for signature, error_data in error_signatures.items():
                test_name = error_data["test_name"]
                results[suite_name][test_name]["log_excerpt"] = [error_data["excerpt"]]
                results[suite_name][test_name]["affected_files"] = sorted(
                    list(error_data["affected_files"])
                )

        return results

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Shared utilities for test code to reduce duplication
"""

import os
from typing import Dict, List, Any, Optional, Callable


def find_tests_by_pattern(tests_dict: Dict[str, Any], pattern: str) -> Dict[str, Any]:
    """Find test entries that match a pattern in their name.

    Args:
        tests_dict: Dictionary of test results (e.g., boot_tests)
        pattern: String pattern to search for in test names (case-insensitive)

    Returns:
        Dictionary of matching test entries
    """
    return {
        name: data
        for name, data in tests_dict.items()
        if pattern.lower() in name.lower()
    }


def find_content_in_tests(
    tests_dict: Dict[str, Any], test_pattern: str, content_patterns: List[str]
) -> bool:
    """Check if any test matching a pattern contains specific content.

    Args:
        tests_dict: Dictionary of test results (e.g., boot_tests)
        test_pattern: String pattern to search for in test names (case-insensitive)
        content_patterns: List of content patterns to search for in log excerpts

    Returns:
        True if any matching test contains any of the content patterns
    """
    matching_tests = find_tests_by_pattern(tests_dict, test_pattern)

    for test_name, test_data in matching_tests.items():
        log_excerpt = test_data.get("log_excerpt", [])
        excerpt_text = " ".join(log_excerpt)

        for pattern in content_patterns:
            if pattern in excerpt_text:
                return True

    return False


def assert_tests_created(
    tests_dict: Dict[str, Any], test_pattern: str, error_message: Optional[str] = None
) -> None:
    """Assert that tests matching a pattern were created.

    Args:
        tests_dict: Dictionary of test results (e.g., boot_tests)
        test_pattern: String pattern to search for in test names (case-insensitive)
        error_message: Custom error message for assertion
    """
    matching_tests = find_tests_by_pattern(tests_dict, test_pattern)
    if error_message is None:
        error_message = f"Should detect {test_pattern} patterns"

    assert len(matching_tests) > 0, error_message


def assert_content_found(
    tests_dict: Dict[str, Any],
    test_pattern: str,
    content_patterns: List[str],
    error_message: Optional[str] = None,
) -> None:
    """Assert that tests matching a pattern contain specific content.

    Args:
        tests_dict: Dictionary of test results (e.g., boot_tests)
        test_pattern: String pattern to search for in test names (case-insensitive)
        content_patterns: List of content patterns to search for in log excerpts
        error_message: Custom error message for assertion
    """
    found = find_content_in_tests(tests_dict, test_pattern, content_patterns)
    if error_message is None:
        error_message = f"Should capture content patterns {content_patterns} in {test_pattern} tests"

    assert found, error_message


def get_parser_results(data: Dict[str, Any], parser_type: str) -> Dict[str, Any]:
    """Get parser results from data, handling different parser key patterns.

    Args:
        data: Parser output data
        parser_type: Type of parser ("boot", "build", "test")

    Returns:
        Dictionary of parser results

    Raises:
        AssertionError: If expected parser results are not found
    """
    if parser_type == "boot":
        # Handle boot parser which might be under log-parser-boot or log-parser-test
        if "log-parser-boot" in data:
            return data["log-parser-boot"]
        elif "log-parser-test" in data:
            return data["log-parser-test"]
        else:
            raise AssertionError(
                f"Should have boot parser results, got keys: {list(data.keys())}"
            )

    elif parser_type == "build":
        # Handle build parser which creates keys like log-parser-build-*
        build_keys = [k for k in data.keys() if k.startswith("log-parser-build")]
        if not build_keys:
            raise AssertionError("Should create build parser results")
        return data[build_keys[0]]

    elif parser_type == "test":
        if "log-parser-test" not in data:
            raise AssertionError("Should create test parser results")
        return data["log-parser-test"]

    else:
        raise ValueError(f"Unknown parser type: {parser_type}")


def read_sample_file(name: str, data_subdir: str = "") -> str:
    """Read sample log files from test data directory.

    Args:
        name: Name of the file to read
        data_subdir: Subdirectory under test/data (e.g., "build", "boot")

    Returns:
        Contents of the file as string
    """
    if not name.startswith("/"):
        # Get the directory where this module is located (test/)
        test_dir = os.path.dirname(__file__)
        if data_subdir:
            name = os.path.join(test_dir, "data", data_subdir, name)
        else:
            name = os.path.join(test_dir, "data", name)

    with open(name, "r") as f:
        return f.read()


def assert_valid_parser_output(data: Any, parser_name: str = "parser") -> None:
    """Assert that parser output is valid.

    Args:
        data: Parser output to validate
        parser_name: Name of parser for error messages
    """
    assert data is not None, f"{parser_name} should return data"
    assert isinstance(data, dict), f"{parser_name} should return dictionary structure"


def parse_and_validate(
    parser: Any, log_content: str, unique: bool = False, parser_name: str = "parser"
) -> Dict[str, Any]:
    """Parse log content and validate output.

    Args:
        parser: Parser instance
        log_content: Log content to parse
        unique: Whether to use unique parsing
        parser_name: Name of parser for error messages

    Returns:
        Validated parser output
    """
    data = parser.parse_log(log_content, unique=unique)
    assert_valid_parser_output(data, parser_name)
    return data


def run_test_scenarios(
    scenarios: List[str],
    test_func: Callable[[str], None],
    scenario_name: str = "scenario",
) -> None:
    """Run a test function against multiple scenarios.

    Args:
        scenarios: List of test scenarios (log content, file names, etc.)
        test_func: Function to call for each scenario
        scenario_name: Name for scenarios in error messages
    """
    for i, scenario in enumerate(scenarios):
        try:
            test_func(scenario)
        except Exception as e:
            raise AssertionError(
                f"Failed on {scenario_name} {i+1}: {scenario[:50]}..."
            ) from e


def assert_no_failures_in_results(
    test_results: Dict[str, Any], context: str = "test results"
) -> None:
    """Assert that no test results have 'fail' status.

    Args:
        test_results: Dictionary of test results
        context: Context description for error messages
    """
    for test_name, test_data in test_results.items():
        result = test_data.get("result", "pass")
        assert (
            result != "fail"
        ), f"Should not have failures in {context}, but {test_name} failed with result {result}"


def count_tests_by_patterns(
    test_results: Dict[str, Any], patterns: List[str]
) -> Dict[str, int]:
    """Count tests matching each pattern.

    Args:
        test_results: Dictionary of test results
        patterns: List of patterns to search for

    Returns:
        Dictionary mapping pattern to count
    """
    counts = {}
    for pattern in patterns:
        counts[pattern] = len(find_tests_by_pattern(test_results, pattern))
    return counts


def assert_multiple_patterns_detected(
    test_results: Dict[str, Any],
    patterns: List[str],
    min_patterns: int = 2,
    context: str = "test results",
) -> None:
    """Assert that multiple different patterns are detected.

    Args:
        test_results: Dictionary of test results
        patterns: List of patterns to check for
        min_patterns: Minimum number of different patterns that should be detected
        context: Context description for error messages
    """
    counts = count_tests_by_patterns(test_results, patterns)
    detected_patterns = [pattern for pattern, count in counts.items() if count > 0]

    assert len(detected_patterns) >= min_patterns, (
        f"Should detect at least {min_patterns} different patterns in {context}, "
        f"detected: {detected_patterns} (counts: {counts})"
    )

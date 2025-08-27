#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: set ts=4
#
# Copyright 2025-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import logging
import yaml

from tuxparse.lib.base_log_parser import (
    BaseLogParser,
)

logger = logging.getLogger()


class LineNumberLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        mapping = super().construct_mapping(node, deep)
        mapping["_line_number"] = node.start_mark.line + 1
        return mapping


class TestParser(BaseLogParser):
    def process_test_suites(self, test_suite, log_excerpt):
        for test_name, test_data in test_suite.items():
            if isinstance(test_data, dict):
                starttc = test_data.get("starttc")
                endtc = test_data.get("endtc")

                if isinstance(starttc, int) and isinstance(endtc, int):
                    test_data["log_excerpt"] = [
                        f"{message}"
                        for line, message, line_number in log_excerpt
                        if starttc <= line_number <= endtc
                    ]

                self.process_test_suites(test_data, log_excerpt)

    def parse_log(self, log_input, unique):
        if log_input is None:
            logger.error("need a log file")
            return {}

        # Handle both string and file object inputs
        if isinstance(log_input, str):
            log_file = log_input
        else:
            # File object input - read content
            log_file = log_input.read()

        if not log_file:
            logger.error("log file is empty")
            return {}

        log_data = yaml.load(log_file, Loader=LineNumberLoader)
        log_excerpt = []
        for entry in log_data:
            if isinstance(entry, dict) and "dt" in entry and "msg" in entry:
                try:
                    line = entry["dt"]
                    message = entry["msg"]
                    line_number = entry.get("_line_number", None)
                    log_excerpt.append((line, message, line_number))
                except ValueError:
                    print(f"Skipping log entry with invalid line: {entry['dt']}")

        # Initialize data structure
        data = {}

        self.process_test_suites(data, log_excerpt)

        return data

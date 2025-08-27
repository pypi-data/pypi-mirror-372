#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: set ts=4
#
# Copyright 2025-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import argparse
import io
import json
import logging
import os
import sys

from tuxparse.boot_test_parser import BootTestParser
from tuxparse.build_parser import BuildParser
from tuxparse.test_parser import TestParser


logger = logging.getLogger()

log_parsers = {
    "boot_test": BootTestParser(),
    "build": BuildParser(),
    "test": TestParser(),
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="TuxParse, parse build, boot/test log files and print the output to the stdout."
    )

    parser.add_argument(
        "--log-file",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="Log file to parser",
    )

    parser.add_argument(
        "--result-file",
        # type=argparse.FileType("rw"),
        default=None,
        help="Result JSON file to read and write too",
    )

    parser.add_argument(
        "--log-parser",
        choices=log_parsers.keys(),
        default="boot_test",
        help="Which log parser to run, when boot_test or build log-file should \
        be logs.txt or build.log, and for test it should be lava-logs.yaml",
    )

    parser.add_argument(
        "--unique",
        action="store_true",
        default=False,
        help="make unique",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Display debug messages",
    )

    args = parser.parse_args()

    if args.log_file is sys.stdin and sys.stdin.isatty():
        parser.error("Error: No input provided via stdin or --log-file. Exiting.")

    return args


def _is_lava_yaml_format(file_obj):
    """Check if file starts with LAVA YAML format without loading entire content"""
    try:
        first_line = file_obj.readline()
        file_obj.seek(0)  # Reset to beginning
        return first_line.strip().startswith("- {") and first_line.strip().endswith("}")
    except (OSError, io.UnsupportedOperation):
        # Non-seekable stream - can't reset, return False for safety
        return False
    except Exception:
        # Any other error - return False for safety
        return False


def main():
    try:
        args = parse_args()
        if args.debug:
            logger.setLevel(level=logging.DEBUG)

        parser = log_parsers[args.log_parser]

        # Handle LAVA YAML preprocessing for boot_test_parser
        if args.log_parser == "boot_test" and _is_lava_yaml_format(args.log_file):
            try:
                # Read content and process LAVA YAML
                content = args.log_file.read()
                processed_content = parser.logs_txt(content)

                # Write debug file
                with open("logs.txt", "w", encoding="utf-8") as f_txt:
                    f_txt.write(processed_content)

                # Create new file object with processed content
                args.log_file = io.StringIO(processed_content)
            except Exception as e:
                logger.error(f"Failed to process LAVA YAML format: {e}")
                return 1

        data = parser.parse_log(args.log_file, args.unique)

        # Print JSON to stdout
        print(json.dumps(data, indent=4))

        if args.result_file:
            if os.path.exists(args.result_file):
                with open(args.result_file, "r") as f:
                    orig_contents = f.read()
                if orig_contents:
                    orig = json.loads(orig_contents)
                    orig.update(data)
                    data = orig
            with open(args.result_file, "w") as f:
                json.dump(data, f, indent=4)
        return 0
    except SystemExit as e:
        # Re-raise SystemExit in normal operation, but allow tests to catch it
        raise e


def start():
    if __name__ == "__main__":
        sys.exit(main())


start()

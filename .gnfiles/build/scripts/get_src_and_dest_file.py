#
# Copyright © 2025 Agora
# This file is part of TEN Framework, an open source project.
# Licensed under the Apache License, Version 2.0, with certain conditions.
# Refer to the "LICENSE" file in the root directory for more information.
#
import argparse
import json
from typing import Optional


class ArgumentInfo(argparse.Namespace):
    def __init__(self):
        self.input_string: str
        # The delimiter that separates the source and the target.
        self.src_dest_delimiter: Optional[str] = None
        # The delimiter that separates the source_base.
        self.src_base_delimiter: Optional[str] = None


def main():
    parser = argparse.ArgumentParser(
        description="Split an input string and return JSON of parts."
    )
    parser.add_argument(
        "--input-string", type=str, required=True, help="String to be split."
    )
    parser.add_argument(
        "--src-dest-delimiter",
        type=str,
        required=False,
        help="Delimiter between source and destination.",
    )
    parser.add_argument(
        "--src-base-delimiter",
        type=str,
        required=False,
        help="Delimiter for source base.",
    )

    arg_info = ArgumentInfo()
    args = parser.parse_args(namespace=arg_info)

    source_base: Optional[str] = None
    source: str = ""
    destination: Optional[str] = None

    remaining_string = args.input_string

    # Handle source_base delimiter if specified.
    if args.src_base_delimiter:
        parts = remaining_string.split(args.src_base_delimiter, 1)
        if len(parts) == 2:
            source_base, remaining_string = parts
        else:
            source_base = None

    # Handle src/dest delimiter if specified.
    if args.src_dest_delimiter:
        parts = remaining_string.split(args.src_dest_delimiter, 1)
        if len(parts) == 2:
            source_part, destination = parts
        else:
            source_part = remaining_string
            destination = None
    else:
        source_part = remaining_string
        destination = None

    # Handle source delimiter if specified.
    source = source_part

    if destination is None:
        destination = source

    response = {
        "source_base": source_base if source_base is not None else "",
        "source": source,
        "destination": destination,
    }

    print(json.dumps(response, indent=2))


if __name__ == "__main__":
    main()

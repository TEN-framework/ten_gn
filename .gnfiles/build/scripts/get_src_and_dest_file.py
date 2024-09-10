#
# This file is part of the TEN Framework project.
# See https://github.com/TEN-framework/ten_framework/LICENSE for license
# information.
#
import argparse
import json
import re


class ArgumentInfo(argparse.Namespace):
    def __init__(self):
        self.input_string: str
        self.delimiter: list[str]


def main():
    parser = argparse.ArgumentParser(
        description="Split an input string and return JSON of parts."
    )
    parser.add_argument(
        "--input-string", type=str, required=True, help="String to be split."
    )
    parser.add_argument(
        "--delimiter",
        type=str,
        required=True,
        action="append",
        help="Delimiter to split the string.",
    )

    arg_info = ArgumentInfo()
    args = parser.parse_args(namespace=arg_info)

    # Combine all delimiters into a single regular expression pattern.
    combined_delimiter = "|".join(map(re.escape, args.delimiter))

    parts = re.split(combined_delimiter, args.input_string)

    response = {}

    # Check if the delimiter was found in the input string.
    if len(parts) == 1 and parts[0] == args.input_string:
        # Delimiter not found, treating the whole string as both source and
        # destination.
        response["sources"] = [args.input_string]
        response["destination"] = args.input_string
    else:
        # Assume the last part is the destination, and the rest are sources.
        response["sources"] = parts[:-1]
        response["destination"] = parts[-1]

    print(json.dumps(response, ensure_ascii=False))


if __name__ == "__main__":
    main()

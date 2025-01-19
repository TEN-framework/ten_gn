#
# Copyright © 2025 Agora
# This file is part of TEN Framework, an open source project.
# Licensed under the Apache License, Version 2.0, with certain conditions.
# Refer to the "LICENSE" file in the root directory for more information.
#
import argparse
import os
import sys
import glob
import json
from typing import Optional


class ArgumentInfo(argparse.Namespace):
    def __init__(self):
        self.src_base: Optional[str] = None
        self.src_base_abs_path: Optional[str] = None
        self.src: str
        self.src_abs_path: str
        self.dest_base: str
        self.dest_base_abs_path: str


def glob_fs_entries(source: str) -> list[str]:
    results: list[str] = []

    for v in glob.glob(source, recursive=True):
        results.append(v.replace("\\", "/"))

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src-base", type=str, required=False)
    parser.add_argument("--src-base-abs-path", type=str, required=False)
    parser.add_argument("--src", type=str, required=True)
    parser.add_argument("--src-abs-path", type=str, required=True)
    parser.add_argument("--dest-base", type=str, required=True)
    parser.add_argument("--dest-base-abs-path", type=str, required=True)

    arg_info = ArgumentInfo()
    args = parser.parse_args(namespace=arg_info)

    if (args.src_base is None) != (args.src_base_abs_path is None):
        print(
            "Error: src_base and src_base_abs_path must both be provided "
            "or both be absent.",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.src_base is None:
        args.src_base = args.src
        args.src_base_abs_path = args.src_abs_path

    result_srcs_abs_path = glob_fs_entries(args.src_abs_path)

    result_srcs: list[str] = []
    result_dests: list[str] = []
    result_dests_abs_path: list[str] = []

    for result_src_abs_path in result_srcs_abs_path:
        # Compute relative path to src_base_abs_path.
        relative_path = os.path.relpath(
            result_src_abs_path, args.src_base_abs_path
        )

        # Ensure consistency in path separators.
        relative_path = relative_path.replace("\\", "/")
        if relative_path == ".":
            relative_path = None

        result_src = args.src_base
        result_dest = args.dest_base
        result_dest_abs_path = args.dest_base_abs_path

        if relative_path:
            result_src = os.path.join(result_src, relative_path)
            result_dest = os.path.join(result_dest, relative_path)
            result_dest_abs_path = os.path.join(
                result_dest_abs_path, relative_path
            )

        result_src = result_src.replace("\\", "/")
        result_srcs.append(result_src)

        result_dest = result_dest.replace("\\", "/")
        result_dests.append(result_dest)

        result_dest_abs_path = result_dest_abs_path.replace("\\", "/")
        result_dests_abs_path.append(result_dest_abs_path)

    output = {
        "sources": result_srcs,
        "sources_abs_path": result_srcs_abs_path,
        "destinations": result_dests,
        "destinations_abs_path": result_dests_abs_path,
    }

    json_output = json.dumps(output, indent=2)
    print(json_output)

    sys.exit(0)


if __name__ == "__main__":
    main()

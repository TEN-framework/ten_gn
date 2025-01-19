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
from dataclasses import dataclass, asdict


class ArgumentInfo(argparse.Namespace):
    def __init__(self):
        self.src_base: str
        self.src_base_abs_path: str
        self.src_abs_path: str
        self.dest_base: str
        self.dest_base_abs_path: str


def contains_glob_char(s: str) -> bool:
    glob_chars = ["*", "?", "[", "]", "{", "}"]
    return any(char in s for char in glob_chars)


def glob_fs_entries(source: str) -> list[str]:
    results: list[str] = []

    for v in glob.glob(source, recursive=True):
        if not os.path.isfile(v):
            continue
        results.append(v.replace("\\", "/"))

    return results


@dataclass
class SrcDestInfo:
    source: str
    source_abs_path: str
    destination: str
    destination_abs_path: str


def glob_src_to_dest(
    src_base: str,
    src_base_abs_path: str,
    src_abs_path: str,
    dest_base: str,
    dest_base_abs_path: str,
) -> list[SrcDestInfo]:
    if contains_glob_char(src_base) or contains_glob_char(src_base_abs_path):
        raise Exception(
            f"src_base `{src_base}` and "
            f"src_base_abs_path `{src_base_abs_path}` "
            "cannot contain glob characters."
        )

    result_srcs_abs_path = glob_fs_entries(src_abs_path)

    result_mapping: list[SrcDestInfo] = []

    for result_src_abs_path in result_srcs_abs_path:
        # Compute relative path to src_base_abs_path.
        relative_path = os.path.relpath(result_src_abs_path, src_base_abs_path)

        # Ensure consistency in path separators.
        relative_path = relative_path.replace("\\", "/")
        if relative_path == ".":
            relative_path = None

        result_src = src_base
        result_dest = dest_base
        result_dest_abs_path = dest_base_abs_path

        if relative_path:
            result_src = os.path.join(result_src, relative_path)
            result_dest = os.path.join(result_dest, relative_path)
            result_dest_abs_path = os.path.join(
                result_dest_abs_path, relative_path
            )

        result_src = result_src.replace("\\", "/")
        result_dest = result_dest.replace("\\", "/")
        result_dest_abs_path = result_dest_abs_path.replace("\\", "/")

        result_mapping.append(
            SrcDestInfo(
                source=result_src,
                source_abs_path=result_src_abs_path,
                destination=result_dest,
                destination_abs_path=result_dest_abs_path,
            )
        )

    return result_mapping


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--src-base", type=str, required=True)
    parser.add_argument("--src-base-abs-path", type=str, required=True)
    parser.add_argument("--src-abs-path", type=str, required=True)
    parser.add_argument("--dest-base", type=str, required=True)
    parser.add_argument("--dest-base-abs-path", type=str, required=True)

    arg_info = ArgumentInfo()
    args = parser.parse_args(namespace=arg_info)

    result_mapping = glob_src_to_dest(
        args.src_base,
        args.src_base_abs_path,
        args.src_abs_path,
        args.dest_base,
        args.dest_base_abs_path,
    )

    json_output = json.dumps(
        [asdict(item) for item in result_mapping], indent=2
    )
    print(json_output)

    sys.exit(0)

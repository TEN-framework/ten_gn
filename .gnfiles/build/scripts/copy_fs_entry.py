#
# Copyright © 2024 Agora
# This file is part of TEN Framework, an open source project.
# Licensed under the Apache License, Version 2.0, with certain conditions.
# Refer to the "LICENSE" file in the root directory for more information.
#
import os
import argparse
from typing import Optional
from build.scripts import fs_utils, timestamp_proxy

""" Copy from the paths of the 1st to N-1 arguments to the path of the Nth
argument.
"""


class ArgumentInfo(argparse.Namespace):
    def __init__(self):
        self.source: list[str]
        self.destination: str
        self.tg_timestamp_proxy_file: Optional[str] = None


def main():
    parser = argparse.ArgumentParser(
        description="Copy source files to destination."
    )
    parser.add_argument(
        "--source", action="append", required=True, help="Source file paths"
    )
    parser.add_argument(
        "--destination", required=True, help="Destination file path"
    )
    parser.add_argument(
        "--tg-timestamp-proxy-file",
        required=False,
        help="Destination file path",
    )

    arg_info = ArgumentInfo()
    args = parser.parse_args(namespace=arg_info)

    src_paths = args.source
    dst = args.destination

    try:
        # Check all the sources are existed.
        for src in src_paths:
            if not os.path.exists(src):
                raise Exception(f"{src} does not exist")

        try:
            # Ensure the destination folder, if specified, does exist.
            if os.path.dirname(dst) != "":
                fs_utils.mkdir_p(os.path.dirname(dst))
        except Exception as e:
            raise Exception(f"Failed to create destination directory: {str(e)}")

        for src in src_paths:
            if src.endswith(timestamp_proxy.TG_TIMESTAMP_PROXY_EXTENSION):
                continue
            try:
                fs_utils.copy(src, dst)
            except Exception as e:
                raise Exception(f"Failed to copy {src} to {dst}: {str(e)}")

        # Touch the tg_timestamp_proxy_file if specified.
        timestamp_proxy.touch_timestamp_proxy_file(args.tg_timestamp_proxy_file)

    except Exception as e:
        timestamp_proxy.remove_timestamp_proxy_file(
            args.tg_timestamp_proxy_file
        )
        raise e


if __name__ == "__main__":
    main()

#
# Copyright © 2025 Agora
# This file is part of TEN Framework, an open source project.
# Licensed under the Apache License, Version 2.0, with certain conditions.
# Refer to the "LICENSE" file in the root directory for more information.
#

# list source files and output files
# Usage:
#   python glob_tsconfig_files.py tsconfig.json         # prints sources
#   python glob_tsconfig_files.py tsconfig.json out_dir # prints outputs

import json
import sys
import re


sys.dont_write_bytecode = True
# proper glob for python 2 & 3


def read_ts_config(file_name):
    with open(file_name) as f:
        ts_config = f.read()

    # Remove comments and redundant commas before JSON parsing, because they
    # are not valid JSON contents.

    str_pattern = r'"(?:\\.|[^"])*"'

    def keep_str_remove_comments(m):
        if m.group(0).startswith("/"):
            return ""
        else:
            return m.group(0)

    ts_config = re.sub(
        str_pattern + r"|/\*[.\n]+?\*/|//[^\n]*",
        keep_str_remove_comments,
        ts_config,
    )

    def keep_str_remove_redundant_commas(m):
        if m.group(0).startswith(","):
            return m.group(0)[1:]
        else:
            return m.group(0)

    ts_config = re.sub(
        str_pattern + r"|,(?:[\s\n]*[\]\}])",
        keep_str_remove_redundant_commas,
        ts_config,
    )

    config = json.loads(ts_config)
    return config


if __name__ == "__main__":
    # outputs depends on tsconfig.json, but not including this file
    ts_config = read_ts_config(sys.argv[1])
    print(ts_config["compilerOptions"]["outDir"])

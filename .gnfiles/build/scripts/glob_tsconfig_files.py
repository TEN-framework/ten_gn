# list source files and output files
# Usage:
#   python glob_tsconfig_files.py tsconfig.json         # prints sources
#   python glob_tsconfig_files.py tsconfig.json out_dir # prints outputs

import json
import sys
import re
import glob
import os
import fnmatch


sys.dont_write_bytecode = True
# proper glob for python 2 & 3


def proper_glob(src_pattern):
    if "**" in src_pattern:
        srcs = []
        folder, pattern = src_pattern.split("**")
        if not folder:
            folder = "."
        pattern = pattern.strip("/")
        for root, dirnames, filenames in os.walk(folder):
            dirnames[:] = [d for d in dirnames if d != "node_modules"]
            for filename in fnmatch.filter(filenames, pattern):
                srcs.append(os.path.join(root, filename))
        return srcs
    else:
        return glob.glob(src_pattern)


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


def glob_ts_sources(ts_config_file, ts_config, out_dir=None):
    # Remember current working directory so that we can come back here.
    dir = os.path.abspath(".")

    try:
        source_folder = os.path.dirname(os.path.abspath(ts_config_file))
        os.chdir(source_folder)

        srcs = []
        if "include" in ts_config:
            for src_pattern in ts_config["include"]:
                srcs += proper_glob(src_pattern)
        else:
            srcs += proper_glob("**/*")

        if "exclude" in ts_config:
            for src_pattern in ts_config["exclude"]:
                new_srcs = []
                exclude_srcs = proper_glob(src_pattern)
                for src in srcs:
                    if src not in exclude_srcs:
                        new_srcs.append(src)
                srcs = new_srcs

        results = []
        for line in srcs:
            if out_dir:
                results.append(
                    out_dir.rstrip("/")
                    + "/"
                    + re.sub(r"\.ts$", ".js", line, re.IGNORECASE)
                )
            else:
                results.append(os.path.join(source_folder, line))

        return results
    finally:
        # Go back to the original working directory.
        os.chdir(dir)


if __name__ == "__main__":
    if len(sys.argv) > 2:
        out_dir = sys.argv[2]
    else:
        out_dir = None
    # outputs depends on tsconfig.json, but not including this file
    if not out_dir:
        print(sys.argv[1])
    ts_config = read_ts_config(sys.argv[1])
    sources = glob_ts_sources(sys.argv[1], ts_config, out_dir)
    for source in sources:
        print(source)
#
# Copyright © 2025 Agora
# This file is part of TEN Framework, an open source project.
# Licensed under the Apache License, Version 2.0, with certain conditions.
# Refer to the "LICENSE" file in the root directory for more information.
#
"""
Get the MinGW bin directory from the compiler path.
"""

import os
import subprocess
import sys


def get_mingw_bin_dir(compiler):
    """Get MinGW bin directory from compiler path."""
    try:
        # Get the full path of the compiler
        result = subprocess.run(
            ["where" if os.name == "nt" else "which", compiler],
            capture_output=True,
            text=True,
            check=True,
        )
        compiler_path = result.stdout.strip().split("\n")[0]

        # Get the directory containing the compiler
        bin_dir = os.path.dirname(compiler_path)

        # Normalize path for Windows
        if os.name == "nt":
            bin_dir = bin_dir.replace("\\", "/")

        #print(f"Found MinGW bin directory: {bin_dir}", file=sys.stderr)
        return bin_dir
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(
            f"Error: Could not find MinGW bin directory for compiler: {compiler}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: get_mingw_bin_dir.py <compiler>", file=sys.stderr)
        sys.exit(1)

    compiler = sys.argv[1]
    print(get_mingw_bin_dir(compiler))

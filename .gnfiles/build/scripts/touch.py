#
# Copyright © 2024 Agora
# This file is part of TEN Framework, an open source project.
# Licensed under the Apache License, Version 2.0, with certain conditions.
# Refer to the "LICENSE" file in the root directory for more information.
#
import sys
import os


def touch(path):
    with open(path, "a"):
        try:
            os.utime(path, follow_symlinks=False)
        except Exception:
            try:
                # If follow_symlinks parameter is not supported, fall back to
                # default behavior
                os.utime(path)
            except Exception:
                exit(1)


if __name__ == "__main__":
    path = sys.argv[1]
    touch(path)

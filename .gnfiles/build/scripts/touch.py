#
# This file is part of the TEN Framework project.
# See https://github.com/TEN-framework/ten_framework/LICENSE for license
# information.
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

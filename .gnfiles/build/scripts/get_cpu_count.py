#
# This file is part of the TEN Framework project.
# See https://github.com/TEN-framework/ten_framework/LICENSE for license
# information.
#
import multiprocessing
import sys


def main():
    try:
        cpu_count = multiprocessing.cpu_count()
    except Exception:
        cpu_count = 1

    print(cpu_count)
    return 0


if __name__ == "__main__":
    sys.exit(main())

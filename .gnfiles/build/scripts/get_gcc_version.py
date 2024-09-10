#
# This file is part of the TEN Framework project.
# See https://github.com/TEN-framework/ten_framework/LICENSE for license
# information.
#
import sys
import subprocess


def main(argv):
    ctx = subprocess.check_output(argv[0] + " --version", shell=True)
    lines = ctx.splitlines()
    version = str(lines[0].strip()).split(" ")[-1]
    if "." not in version:
        version = str(lines[0].strip()).split(" ")[-2]
    version_numbers = version.split(".")
    print(version_numbers[0])


if __name__ == "__main__":
    main(sys.argv[1:])

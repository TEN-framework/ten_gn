#
# This file is part of the TEN Framework project.
# See https://github.com/TEN-framework/ten_framework/LICENSE for license
# information.
#
import os
import sys


def main(argv):
    if len(argv) != 0:
        raise Exception("Invalid parameter")
    dir_name = os.path.dirname(os.path.abspath(__file__))

    dir_name = os.path.join(dir_name, "..", "..", "bin")
    if sys.platform == "win32":
        dir_name = os.path.join(dir_name, "win", "ninja.exe")
        dir_name = os.path.abspath(dir_name).replace("\\", "/")
    elif sys.platform == "darwin":
        dir_name = os.path.join(dir_name, "mac", "ninja")
        dir_name = os.path.abspath(dir_name)
    else:
        dir_name = os.path.join(dir_name, "linux", "ninja")
        dir_name = os.path.abspath(dir_name)

    sys.stdout.write(dir_name)
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])

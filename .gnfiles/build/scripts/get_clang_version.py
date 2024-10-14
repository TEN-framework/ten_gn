#
# Copyright © 2024 Agora
# This file is part of TEN Framework, an open source project.
# Licensed under the Apache License, Version 2.0, with certain conditions.
# Refer to the "LICENSE" file in the root directory for more information.
#
import sys
import subprocess
import re

"""
# linux
Ubuntu clang version 14.0.0-1ubuntu1.1
# mac
Apple clang version 15.0.0 (clang-1500.3.9.4)
# win
clang version 14.0.1
"""

def main(argv):
    version_string = subprocess.check_output(argv[0] + " --version", shell=True).decode('utf-8')
    match = re.search(r'clang version (\d+)', version_string)
    if match:
        print(match.group(1))
        return
    print("")


if __name__ == "__main__":
    main(sys.argv[1:])

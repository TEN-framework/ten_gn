#
# Copyright © 2024 Agora
# This file is part of TEN Framework, an open source project.
# Licensed under the Apache License, Version 2.0, with certain conditions.
# Refer to the "LICENSE" file in the root directory for more information.
#
import os
import sys
import subprocess
from build.scripts import fs_utils, log, cmd_exec
import argparse


class NpmInstall:
    def __init__(self, args) -> None:
        self.args = args
        self.show_extra_log(
            "npm_install.py\n              project_dir:"
            f" {self.args.project_dir}\n              tsconfig:"
            f" {self.args.package_json}\n              output_dir:"
            f" {self.args.output_dir}\n              platform:"
            f" {self.args.platform}"
        )

    def show_extra_log(self, str):
        if self.args.log_level >= 1:
            log.info(str)

    def tsc_exist(self):
        cmd = "tsc --version"
        status, _ = cmd_exec.run_cmd_realtime(
            cmd, log_level=self.args.log_level
        )
        if status == 0:
            return True

        if sys.platform == "win32":
            tsc = os.path.join("node_modules", ".bin", "tsc.cmd")
        else:
            tsc = os.path.join("node_modules", ".bin", "tsc")

        if os.path.exists(tsc):
            return True
        else:
            return False

    def check_npm_version(self):
        if sys.platform == "win32":
            my_cmd = ["cmd", "/c", "npm", "--version"]
        else:
            my_cmd = ["npm", "--version"]
        child = subprocess.Popen(
            my_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            encoding="utf-8",
        )
        stdout, stderr = child.communicate()
        if child.returncode:
            log.error(f"Stderr:\n{stderr}")
            exit(-1)
        if int(stdout.split(".")[0]) < 8:
            log.error("Your npm version less than 8, please upgrade")
            exit(-1)

    def install(self):
        os.chdir(args.output_dir)
        for i in range(3):
            try:
                if os.path.exists("package-lock.json"):
                    if not os.path.exists("node_modules") or os.path.getmtime(
                        "package-lock.json"
                    ) > os.path.getmtime("node_modules"):
                        # npm ci: fail if lock file not satisfied
                        self.show_extra_log(
                            "npm install (npm ci), because package-lock.json"
                            " exists."
                        )

                        cmd = "npm ci"
                        if self.args.log_level == 1:
                            cmd += " --loglevel verbose"
                        elif self.args.log_level == 2:
                            cmd += " --loglevel silly"

                        cmd_exec.run_cmd_realtime(
                            cmd, log_level=self.args.log_level
                        )
                    else:
                        self.show_extra_log(
                            "npm skip install (npm i), because"
                            " package-lock.json mtime:"
                            f" {os.path.getmtime('package-lock.json')} <"
                            " node_modules mtime"
                            f" {os.path.getmtime('node_modules')}"
                        )

                        # If tsc not found, we should update package-lock.json
                        # mtime and call npm ci again
                        if not self.tsc_exist():
                            os.utime("package-lock.json")
                else:
                    self.show_extra_log(
                        "npm install (npm i), because package-lock.json not"
                        " exists."
                    )

                    cmd = "npm install"
                    if self.args.log_level == 1:
                        cmd += " --loglevel verbose"
                    elif self.args.log_level == 2:
                        cmd += " --loglevel silly"

                    cmd_exec.run_cmd_realtime(
                        cmd, log_level=self.args.log_level
                    )
            except Exception as exc:
                self.show_extra_log(f"Failed to npm install: {exc}")
            else:
                self.show_extra_log("npm install success.")
                break
        if not self.tsc_exist():
            raise Exception(
                "tsc not found in current npm package and global node dir,"
                " please check"
            )

    def run(self):
        fs_utils.copy(
            self.args.package_json,
            os.path.join(self.args.output_dir, "package.json"),
        )
        if self.args.package_lock_json:
            fs_utils.copy(
                self.args.package_lock_json,
                os.path.join(self.args.output_dir, "package-lock.json"),
            )
        self.check_npm_version()
        self.install()


parser = argparse.ArgumentParser()
parser.add_argument("-project_dir", "--project_dir", type=str, required=True)
parser.add_argument("-package_json", "--package_json", type=str, required=True)
parser.add_argument(
    "-package_lock_json", "--package_lock_json", type=str, required=False
)
parser.add_argument("-output_dir", "--output_dir", type=str, required=True)
parser.add_argument("-platform", "--platform", type=str, required=True)
parser.add_argument(
    "-log_level", "--log_level", type=int, default=0, required=True
)
args = parser.parse_args()

ni = NpmInstall(args)
ni.run()
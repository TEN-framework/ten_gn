#
# Copyright © 2025 Agora
# This file is part of TEN Framework, an open source project.
# Licensed under the Apache License, Version 2.0, with certain conditions.
# Refer to the "LICENSE" file in the root directory for more information.
#
import json
import os
from importlib import machinery
import argparse
from build.scripts import fs_utils, log, cmd_exec

glob_tsconfig_files = machinery.SourceFileLoader(
    "glob_tsconfig_files",
    os.path.dirname(os.path.abspath(__file__)) + "/glob_tsconfig_files.py",
).load_module()


class NpmRunBuild:
    def __init__(self, args) -> None:
        self.args = args
        self.show_extra_log(
            "npm_run_build.py\n"
            f"  project_dir: {args.project_dir}\n"
            f"  tsconfig: {args.tsconfig_file}\n"
            f"  out_dir: {args.out_dir}\n"
            f"  ref: {args.ref}\n"
            f"  platform: {args.platform}\n"
            f"  remove_node_modules: {args.remove_node_modules}\n"
            f"  remove_tsbuildinfo: {args.remove_tsbuildinfo}\n"
            f"  remove_src: {args.remove_src}\n"
        )

    def show_extra_log(self, str: str) -> None:
        if self.args.log_level >= 1:
            log.info(str)

    def sync_source(self, tsconfig) -> None:
        tsconfig_dir = os.path.dirname(self.args.tsconfig_file)

        self.show_extra_log(
            f"Sync sources: {tsconfig_dir} => {self.args.out_dir}"
        )

        sources = glob_tsconfig_files.glob_ts_sources(
            self.args.tsconfig_file, tsconfig
        )

        if os.path.abspath(tsconfig_dir) != os.path.abspath(self.args.out_dir):
            # Do not remove '/build', because we have enabled the incremental
            # build of tsc, so that the files in '/build' might not be
            # re-generated.
            #
            # common_utils.remove_tree(prj_root_dir + "/build")
            fs_utils.remove_tree(self.args.out_dir + "/src")
        for src in sources:
            dst = os.path.relpath(src, tsconfig_dir)
            dst = os.path.join(self.args.out_dir, dst)  # build/../src/**/*
            fs_utils.mkdir_p(os.path.dirname(dst))
            fs_utils.copy(src, dst)
        fs_utils.copy(
            self.args.tsconfig_file,
            os.path.join(self.args.out_dir, "tsconfig.json"),
        )

    # Writes new prj_root_dir/tsconfig.json.
    def dump_new_tsconfig(self, tsconfig_info):
        tsconfig_info["compilerOptions"]["outDir"] = (
            self.args.out_dir + "/build"
        )
        if len(self.args.ref) > 1:
            ref_name_paths = [r.split("=>") for r in self.args.ref.split(",")]
            if "paths" not in tsconfig_info["compilerOptions"].keys():
                tsconfig_info["compilerOptions"]["paths"] = {}
            tsconfig_info["references"] = []
            for name, path in ref_name_paths:
                tsconfig_info["compilerOptions"]["paths"][name] = [path]
                tsconfig_info["references"].append({"path": path})
        out_tsconfig = self.args.out_dir + "/tsconfig.json"
        with open(out_tsconfig, "w") as f:
            log.info("Dump {0}".format(out_tsconfig))
            json.dump(tsconfig_info, f)

    def remove_new_tsconfig(self, prj_root_dir):
        os.remove(prj_root_dir + "/tsconfig.json")

    def npm_run_build(self):
        cmd = ["npm", "run", self.args.build_target]
        if self.args.log_level == 1:
            cmd += ["--loglevel", "timing"]
        elif self.args.log_level == 2:
            cmd += ["--loglevel", "info"]

        if len(self.args.extra_args) > 0:
            cmd += ["--", " ".join(self.args.extra_args)]
        self.show_extra_log(" ".join(cmd))
        cmd_exec.run_cmd_realtime(cmd, log_level=self.args.log_level)

    def cleanup(self):
        self.show_extra_log("Compile done, cleanup")

        if self.args.remove_node_modules and os.path.exists("node_modules"):
            fs_utils.remove_tree("node_modules")

        if self.args.remove_tsbuildinfo and os.path.exists(
            "tsconfig.tsbuildinfo"
        ):
            os.remove("tsconfig.tsbuildinfo")

        if self.args.remove_src and os.path.exists("src"):
            fs_utils.remove_tree("src")

    def generate_path_json(self):
        if self.args.library_path:
            # write path to path.json, which can be used by webpack or other typescript build tool
            with open(os.path.join(self.args.out_dir, "path.json"), "w") as f:
                path_content = {}
                path_content["PROD_APP_DIR"] = os.path.dirname(
                    args.library_path
                )
                json.dump(path_content, f)

    def run(self):
        fs_utils.mkdir_p(os.path.join(self.args.out_dir, "build"))
        cur_path = os.path.abspath(os.path.curdir)
        os.chdir(self.args.out_dir)
        tsconfig_info = glob_tsconfig_files.read_ts_config(
            self.args.tsconfig_file
        )
        self.sync_source(tsconfig_info)
        self.dump_new_tsconfig(tsconfig_info)
        # Before running 'npm run build', we need to generate a special `path.
        # json` file first.
        self.generate_path_json()
        self.npm_run_build()
        self.cleanup()
        os.chdir(cur_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", type=str, required=True)
    parser.add_argument("--tsconfi-file", type=str, required=True)
    parser.add_argument("--out-dir", type=str, required=True)
    parser.add_argument("--ref", type=str, required=False, default="-")
    parser.add_argument("--platform", type=str, required=True)
    parser.add_argument("--library-path", type=str, required=False)
    parser.add_argument("--remove-node_modules", type=bool, default=False)
    parser.add_argument("--remove-tsbuildinfo", type=bool, default=False)
    parser.add_argument("--remove-src", type=bool, default=False)
    parser.add_argument(
        "--build-target", default="build", type=str, required=False
    )
    parser.add_argument("--log-level", default=0, type=int, required=False)
    parser.add_argument(
        "--extra-args", default=[], required=False, action="append"
    )
    args = parser.parse_args()

    nrb = NpmRunBuild(args)
    nrb.run()

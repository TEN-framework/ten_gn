#
#
# Agora Real Time Engagement
# Created by Wei Hu in 2022-06.
# Copyright (c) 2023 Agora IO. All rights reserved.
#
#
import json
import os
from build.scripts import fs_utils, log, cmd_exec
from importlib import machinery
import argparse

glob_tsconfig_files = machinery.SourceFileLoader(
    "glob_tsconfig_files",
    os.path.dirname(os.path.abspath(__file__)) + "/glob_tsconfig_files.py",
).load_module()


class NpmRunBuild:
    def __init__(self, args):
        self.args = args
        self.show_extra_log(
            "npm_run_build.py\n  project_dir: {0}\n  tsconfig: {1}\n  out_dir:"
            " {2}\n  ref: {3}\n  platform: {4}\n  remove_node_modules: {5}\n "
            " remove_tsbuildinfo: {6}\n  remove_src: {7}".format(
                args.project_dir,
                args.tsconfig_file,
                args.out_dir,
                args.ref,
                args.platform,
                args.remove_node_modules,
                args.remove_tsbuildinfo,
                args.remove_src,
            )
        )

    def show_extra_log(self, str):
        if self.args.log_level >= 1:
            log.info(str)

    def sync_source(self, tsconfig):
        tsconfig_dir = os.path.dirname(self.args.tsconfig_file)

        self.show_extra_log(
            "Sync sources: {0} => {1}".format(tsconfig_dir, self.args.out_dir)
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

    # Writes new prj_root_dir/tsconfig.json

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


parser = argparse.ArgumentParser()
parser.add_argument("-project_dir", "--project_dir", type=str, required=True)
parser.add_argument(
    "-tsconfig_file", "--tsconfig_file", type=str, required=True
)
parser.add_argument("-out_dir", "--out_dir", type=str, required=True)
parser.add_argument("-ref", "--ref", type=str, required=False, default="-")
parser.add_argument("-platform", "--platform", type=str, required=True)
parser.add_argument("-library_path", "--library_path", type=str, required=False)
parser.add_argument(
    "-remove_node_modules", "--remove_node_modules", type=bool, default=False
)
parser.add_argument(
    "-remove_tsbuildinfo", "--remove_tsbuildinfo", type=bool, default=False
)
parser.add_argument("-remove_src", "--remove_src", type=bool, default=False)
parser.add_argument(
    "-build_target", "--build_target", default="build", type=str, required=False
)
parser.add_argument(
    "-log_level", "--log_level", default=0, type=int, required=False
)
parser.add_argument(
    "-extra_args", "--extra_args", default=[], required=False, action="append"
)
args = parser.parse_args()

nrb = NpmRunBuild(args)
nrb.run()

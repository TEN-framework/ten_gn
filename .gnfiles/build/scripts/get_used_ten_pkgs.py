#
# Copyright © 2024 Agora
# This file is part of TEN Framework, an open source project.
# Licensed under the Apache License, Version 2.0, with certain conditions.
# Refer to the "LICENSE" file in the root directory for more information.
#
import argparse
import json
import os


class ArgumentInfo(argparse.Namespace):
    def __init__(self):
        self.pkg_base_dir: str
        self.app_base_dir: str
        self.pkg_type: list[str]


def filter_folders_with_buildgn(
    base_path: str, subfolders: list[str]
) -> list[str]:
    folders_with_buildgn = []
    for folder in subfolders:
        full_path = os.path.join(base_path, folder)
        if os.path.isfile(os.path.join(full_path, "BUILD.gn")):
            folders_with_buildgn.append(folder)
    return folders_with_buildgn


def load_manifest_dependencies(pkg_base_dir: str) -> list[dict]:
    manifest_path = os.path.join(pkg_base_dir, "manifest.json")
    if os.path.isfile(manifest_path):
        with open(manifest_path, "r") as f:
            manifest_data = json.load(f)
            if "dependencies" in manifest_data:
                return manifest_data["dependencies"]
    return []


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--app-base-dir", type=str, required=True)
    parser.add_argument("--pkg-base-dir", type=str, required=True)
    parser.add_argument("--pkg-type", type=str, required=True, action="append")
    arg_info = ArgumentInfo()
    args = parser.parse_args(namespace=arg_info)

    dependencies = load_manifest_dependencies(args.pkg_base_dir)

    ten_pkg_type_dirs_info = {
        "ten_packages": args.pkg_type,
    }

    matching_folders = []

    for (
        ten_packages,
        ten_pkg_type_dirs,
    ) in ten_pkg_type_dirs_info.items():
        for ten_pkg_type_dir in ten_pkg_type_dirs:
            ten_pkg_type_path = os.path.join(
                args.app_base_dir, ten_packages, ten_pkg_type_dir
            )

            if os.path.isdir(ten_pkg_type_path):
                # List all sub-directories in this directory.
                ten_pkg_paths = [
                    f
                    for f in os.listdir(ten_pkg_type_path)
                    if os.path.isdir(os.path.join(ten_pkg_type_path, f))
                ]

                # Filter subdirectories that contain a BUILD.gn file.
                ten_pkg_dirs_with_buildgn = filter_folders_with_buildgn(
                    ten_pkg_type_path, ten_pkg_paths
                )

                # Check if the subfolder matches any dependency name and type.
                for ten_pkg_dir in ten_pkg_dirs_with_buildgn:
                    for dep in dependencies:
                        if (
                            ten_pkg_dir == dep["name"]
                            and ten_pkg_type_dir == dep["type"]
                        ):
                            matching_folders.append(
                                (
                                    f"{ten_packages}/"
                                    f"{ten_pkg_type_dir}/"
                                    f"{ten_pkg_dir}"
                                )
                            )

    # Print the matching subfolders.
    for ten_pkg_dir in matching_folders:
        print(ten_pkg_dir)

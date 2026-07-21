#
# Copyright © 2025 Agora
# This file is part of TEN Framework, an open source project.
# Licensed under the Apache License, Version 2.0, with certain conditions.
# Refer to the "LICENSE" file in the root directory for more information.
#
import os
import sys
import subprocess


SUPPORTED_VS_VERSIONS = ("2017", "2019", "2022", "2026")


def GetVsPathFromEnv() -> str | None:
    # GitHub Windows runners may already have a newer Visual Studio initialized
    # by msvc-dev-cmd (for example VS 18 / 2026). Prefer the configured install
    # directory when present instead of re-detecting by a hard-coded year path.
    vs_path = os.environ.get("VSINSTALLDIR")
    if not vs_path:
        return None

    vs_path = os.path.normpath(vs_path.rstrip("\\/"))
    if os.path.exists(vs_path):
        return vs_path

    return None


def GetVsPath(version: str) -> str:
    vs_path_from_env = GetVsPathFromEnv()
    if vs_path_from_env:
        return vs_path_from_env

    version_dir_candidates = [version]
    for letter in ["c:", "d:", "e:", "f:", "g:", "h:", "i:", "j:", "k:"]:
        for version_dir in version_dir_candidates:
            for vs_type in ["Community", "Professional", "Enterprise", "BuildTools"]:
                vs_path = (
                    letter
                    + "\\Program Files (x86)\\Microsoft Visual Studio"
                    + "\\{0}\\{1}".format(version_dir, vs_type)
                )
                if os.path.exists(vs_path):
                    return vs_path

                vs_path = (
                    letter
                    + "\\Program Files\\Microsoft Visual Studio\\{0}\\{1}".format(
                        version_dir, vs_type
                    )
                )
                if os.path.exists(vs_path):
                    return vs_path

    raise RuntimeError("No Visual Studio {} detected".format(version))


def main(argc: int, argv: list[str]) -> int:
    if argc != 4:
        raise ValueError(
            "Wrong argument: setup_vs.py [vs version] [host cpu] [target cpu]"
            " [output file]"
        )

    vs_version = argv[0]
    if vs_version not in SUPPORTED_VS_VERSIONS:
        raise ValueError(
            "Only support vs "
            + ", ".join(sorted(SUPPORTED_VS_VERSIONS, key=int))
        )

    host_cpu = argv[1]
    if host_cpu not in ["x86", "x64"]:
        raise ValueError(
            "Currently only support x86 and x64, arm for Windows will be"
            " supported later"
        )

    target_cpu = argv[2]
    if target_cpu not in ["x86", "x64", "arm64"]:
        raise ValueError(
            "Currently only support x86, x64 and arm64, arm for Windows will be"
            " supported later"
        )

    output_file = argv[3]
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if os.path.exists(output_file):
        os.unlink(output_file)

    vs_path = GetVsPath(vs_version)

    vcvarbat = ""
    if host_cpu != target_cpu:
        # Cross compile.
        if target_cpu == "x86":
            vcvarbat = os.path.join(
                vs_path, "VC", "Auxiliary", "Build", "vcvarsamd64_x86.bat"
            )
        elif target_cpu == "x64":
            vcvarbat = os.path.join(
                vs_path, "VC", "Auxiliary", "Build", "vcvarsx86_amd64.bat"
            )
        elif target_cpu == "arm64":
            vcvarbat = os.path.join(
                vs_path, "VC", "Auxiliary", "Build", "vcvarsx86_arm64.bat"
            )
    else:
        if target_cpu == "x86":
            vcvarbat = os.path.join(
                vs_path, "VC", "Auxiliary", "Build", "vcvars86.bat"
            )
        elif target_cpu == "x64":
            vcvarbat = os.path.join(
                vs_path, "VC", "Auxiliary", "Build", "vcvars64.bat"
            )

    tmp_bat = os.path.abspath(os.path.join(output_dir, "____tmp.bat"))
    tmp_env = os.path.abspath(os.path.join(output_dir, "____tmp.txt"))
    with open(tmp_bat, "w", encoding="utf-8") as f:
        f.writelines(
            ['call "{}"\n'.format(vcvarbat), 'set > "{}"\n'.format(tmp_env)]
        )
    subprocess.check_output(tmp_bat)
    os.unlink(tmp_bat)
    if not os.path.exists(tmp_env):
        raise RuntimeError("Setup environment fail")

    with open(tmp_env, "r", encoding="utf-8") as in_file:
        with open(output_file, "wb") as out_file:
            byte_arr = [0]
            binary_format = bytearray(byte_arr)
            lines = in_file.readlines()
            for line in lines:
                out_file.write(line.strip().encode("UTF-8"))
                out_file.write(binary_format)

    os.unlink(tmp_env)
    return 0


if __name__ == "__main__":
    sys.exit(main(len(sys.argv) - 1, sys.argv[1:]))

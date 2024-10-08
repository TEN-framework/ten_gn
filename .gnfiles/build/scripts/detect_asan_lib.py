#
# Copyright © 2024 Agora
# This file is part of TEN Framework, an open source project.
# Licensed under the Apache License, Version 2.0, with certain conditions.
# Refer to the "LICENSE" file in the root directory for more information.
#
import subprocess
import os


def detect_mac_asan_lib(arch: str) -> str:
    if arch == "x64":
        out, _ = subprocess.Popen(
            "clang -m64 -print-file-name=libclang_rt.asan_osx_dynamic.dylib",
            shell=True,
            stdout=subprocess.PIPE,
            encoding="utf-8",
        ).communicate()
    elif arch == "x86":
        out, _ = subprocess.Popen(
            "clang -m32 -print-file-name=libclang_rt.asan_osx_dynamic.dylib",
            shell=True,
            stdout=subprocess.PIPE,
            encoding="utf-8",
        ).communicate()
    elif arch == "arm64":
        out, _ = subprocess.Popen(
            "clang -m64 -print-file-name=libclang_rt.asan_osx_dynamic.dylib",
            shell=True,
            stdout=subprocess.PIPE,
            encoding="utf-8",
        ).communicate()

    libasan_path = out.strip()

    if not libasan_path:
        raise Exception("Failed to find libclang_rt.asan_osx_dynamic.dylib")

    real_libasan_path = os.path.realpath(libasan_path)

    return real_libasan_path


def detect_linux_asan_lib(arch: str) -> str:
    if arch == "x64":
        out, _ = subprocess.Popen(
            "gcc -print-file-name=libasan.so",
            shell=True,
            stdout=subprocess.PIPE,
            encoding="utf-8",
        ).communicate()
    elif arch == "x86":
        out, _ = subprocess.Popen(
            "gcc -m32 -print-file-name=libasan.so",
            shell=True,
            stdout=subprocess.PIPE,
            encoding="utf-8",
        ).communicate()

    libasan_path = out.strip()

    if not libasan_path:
        raise Exception("Failed to find libasan.so")

    real_libasan_path = os.path.realpath(libasan_path)

    return real_libasan_path


# Generally speaking, this function should not need to be called because Clang's
# default ASan mechanism is static linking.
def detect_linux_clang_asan_lib(_arch: str) -> str:
    out, _ = subprocess.Popen(
        "clang -print-file-name=libclang_rt.asan-x86_64.so",
        shell=True,
        stdout=subprocess.PIPE,
        encoding="utf-8",
    ).communicate()

    libasan_path = out.strip()

    if not libasan_path:
        raise Exception("Failed to find libclang_rt.asan-x86_64.so")

    real_libasan_path = os.path.realpath(libasan_path)

    return real_libasan_path

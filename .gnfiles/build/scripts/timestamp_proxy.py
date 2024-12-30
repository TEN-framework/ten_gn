#
# Copyright © 2025 Agora
# This file is part of TEN Framework, an open source project.
# Licensed under the Apache License, Version 2.0, with certain conditions.
# Refer to the "LICENSE" file in the root directory for more information.
#
import os
from typing import Optional
from build.scripts import touch

TG_TIMESTAMP_PROXY_EXTENSION = ".tg_timestamp_proxy"


def _gen_timestamp_proxy_path(path: Optional[str]) -> Optional[str]:
    if path:
        return path + TG_TIMESTAMP_PROXY_EXTENSION
    else:
        return None


def touch_timestamp_proxy_file(path: Optional[str]) -> None:
    path = _gen_timestamp_proxy_path(path)

    if path:
        try:
            touch.touch(path)
        except Exception as e:
            raise Exception(f"Failed to touch timestamp proxy file: {str(e)}")


def remove_timestamp_proxy_file(path: Optional[str]) -> None:
    path = _gen_timestamp_proxy_path(path)

    if path and os.path.exists(path):
        os.remove(path)

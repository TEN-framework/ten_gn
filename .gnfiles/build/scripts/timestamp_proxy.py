#
# This file is part of the TEN Framework project.
# See https://github.com/TEN-framework/ten_framework/LICENSE for license
# information.
#
import os
from build.scripts import touch

TG_TIMESTAMP_PROXY_EXTENSION = ".tg_timestamp_proxy"


def _gen_timestamp_proxy_path(path: str | None) -> str | None:
    if path:
        return path + TG_TIMESTAMP_PROXY_EXTENSION
    else:
        return None


def touch_timestamp_proxy_file(path: str | None) -> None:
    path = _gen_timestamp_proxy_path(path)

    if path:
        try:
            touch.touch(path)
        except Exception as e:
            raise Exception(f"Failed to touch timestamp proxy file: {str(e)}")


def remove_timestamp_proxy_file(path: str | None) -> None:
    path = _gen_timestamp_proxy_path(path)

    if path and os.path.exists(path):
        os.remove(path)

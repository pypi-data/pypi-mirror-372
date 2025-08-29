#
# ML expert Platform
# Copyright (c) 2025-present NAVER Cloud Corp.
# Apache-2.0
#

import fnmatch
import os
from pathlib import Path
from typing import List


def walk(local_path: str, remote_path: str, excludes: List[str] = []):
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"{local_path} not found.")

    if os.path.isfile(local_path):
        if os.path.isdir(remote_path) or remote_path.endswith("/"):
            rfile = os.path.join(remote_path, os.path.basename(local_path))
        else:
            rfile = remote_path
        yield local_path, Path(rfile).as_posix()
        return

    for dirpath, filename in _walk_in_dir(local_path, [*excludes, *DEFAULT_EXCLUDES]):
        local_file = os.path.join(dirpath, filename)
        remote_file = os.path.join(remote_path, os.path.relpath(local_file, local_path))
        yield local_file, Path(remote_file).as_posix()


def _walk_in_dir(local_path, excludes):
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"{local_path} not found.")
    if not os.path.isdir(local_path):
        raise FileNotFoundError("local_path should be a directory.")

    for dirpath, dirs, files in os.walk(local_path, topdown=True):
        dirs[:] = _filter_files(dirs, excludes)
        files[:] = _filter_files(files, excludes)
        for f in files:
            yield dirpath, f


def _filter_files(
    names: List[str],
    excludes: List[str],
) -> List[str]:
    ret = names
    for pat in excludes:
        ret = [r for r in ret if not fnmatch.fnmatch(r, pat)]
    return ret


DEFAULT_EXCLUDES = [
    ".git",
    ".idea",
    ".vscode",
    "__pycache__",
    ".DS_Store",
    "Thumbs.db",
    ".mypy_cache",
    ".eggs",
    ".venv",
    ".pytest_cache",
]

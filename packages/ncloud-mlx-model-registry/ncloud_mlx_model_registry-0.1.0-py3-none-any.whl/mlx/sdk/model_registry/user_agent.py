#
# ML expert Platform
# Copyright (c) 2025-present NAVER Cloud Corp.
# Apache-2.0
#

import sys

from .version import __version__

PYTHON_VERSION = (
    f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
)
USER_AGENT = f"MLX/{__version__} Python/{PYTHON_VERSION}"

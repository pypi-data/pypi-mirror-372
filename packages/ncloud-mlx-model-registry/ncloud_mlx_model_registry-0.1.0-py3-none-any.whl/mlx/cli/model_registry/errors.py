#
# ML expert Platform
# Copyright (c) 2025-present NAVER Cloud Corp.
# Apache-2.0
#

class Error(Exception):
    """Base Error of mlx"""

    pass


empty_error_msg_template = "{0} is not set. Please set '{1}' environment variable or run the '{2}' command to set your {0}."


class EmptyCurrentProjectError(Error):
    """Raised when current project context is empty"""

    def __init__(
        self,
        message=empty_error_msg_template.format(
            "Project", "MLX_PROJECT", "mlx project set"
        ),
    ):
        self.message = message
        super().__init__(self.message)

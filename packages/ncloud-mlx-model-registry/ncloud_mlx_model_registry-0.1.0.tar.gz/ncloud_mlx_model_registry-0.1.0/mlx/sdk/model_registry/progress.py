#
# ML expert Platform
# Copyright (c) 2025-present NAVER Cloud Corp.
# Apache-2.0
#

import atexit
from typing import Callable, Optional

from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    SpinnerColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from rich.progress import Progress as RichProgress


class Progress:
    def total(self, n: int):
        pass

    def completed(self, n: int):
        pass

    def update(self, n: int):
        pass

    def log(self, msg: str):
        pass

    def close(self, description: str = ""):
        pass


class ProgressBar(Progress):
    def __init__(
        self,
        description: str,
        call_back: Optional[Callable[[int, int], None]] = None,
        debug: bool = False,
    ):
        self.debug = debug
        self.description = description
        self.progress = RichProgress(
            SpinnerColumn(),
            "[progress.description]{task.description}",
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.1f}%",
            "•",
            DownloadColumn(),
            "•",
            TransferSpeedColumn(),
            "•",
            TimeRemainingColumn(),
            "•",
            TimeElapsedColumn(),
            console=Console(
                log_path=self.debug,
                force_interactive=not self.debug,
                force_terminal=not self.debug,
            ),
        )
        self.call_back = call_back
        self.last_callback_percentage = 0

        self.is_closed = False
        atexit.register(self.close)

    def total(self, n: int):
        self.task = self.progress.add_task(self.description, total=n)
        self.progress.start()
        self.total_size = n
        self.progressed_size = 0

    def completed(self, n: int):
        self.progress.update(self.task, completed=n)

    def update(self, n: int):
        self.progress.advance(self.task, n)

        self.progressed_size += n
        if self.call_back:
            callback_percentage = int((self.progressed_size / self.total_size) * 1000)
            if self.last_callback_percentage < callback_percentage:
                # To avoid progressed_size > total_size when download/upload retying,
                # set progressed_size to total_size if it is greater than total_size
                progressed_size = min(self.progressed_size, self.total_size)

                self.call_back(progressed_size, self.total_size)
                self.last_callback_percentage = callback_percentage

    def log(self, msg: str):
        self.progress.log(msg)

    def close(self, description: str = ""):
        if description:
            self.progress.update(self.task, description=description)

        if not self.is_closed:
            self.progress.stop()
            self.is_closed = True

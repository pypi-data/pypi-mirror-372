#
# ML expert Platform
# Copyright (c) 2025-present NAVER Cloud Corp.
# Apache-2.0
#

from io import IOBase
from typing import Union

import aiofiles

from .progress import Progress


class FileWriterWithProgress:
    def __init__(
        self,
        filepath: str,
        start: int,
        end: int,
        progress: Union[Progress, None] = None,
    ):
        self.filepath = filepath
        self.start = start
        self.end = end
        self.progress = progress

    def open(self):
        if self.end < self.start:
            raise RuntimeError(f"start({self.start}) is greater then end({self.end})")
        self.file = open(self.filepath, "wb+")
        self.file.seek(self.start)

    def close(self):
        self.file.close()

    def write(self, s: Union[bytes, bytearray]) -> int:
        ret = self.file.write(s)
        self.progress and self.progress.update(ret)
        return ret

    def __enter__(self) -> "FileWriterWithProgress":
        self.open()
        return self

    def __exit__(self, type, value, traceback) -> None:
        self.close()


class AsyncFileReaderWithProgress:
    def __init__(
        self,
        data: Union[str, IOBase],
        start: int,
        end: int,
        progress: Union[Progress, None] = None,
    ):
        self.data = data
        self.start = start
        self.current = start
        self.end = end
        self.progress = progress
        self.is_owned_data = False

    async def open(self):
        self.blksize = 1024 * 1024  # 1MB

        if self.end < self.start:
            raise RuntimeError(f"start({self.start}) is greater then end({self.end})")

        if isinstance(self.data, str):
            self.file = await aiofiles.open(self.data, "rb", buffering=self.blksize)
            self.is_owned_data = True
            await self.file.seek(self.start)
        else:
            self.file = self.data  # TODO: AsyncIterable
            self.is_owned_data = False
            self.file.seek(self.start)

    async def close(self):
        if not self.is_owned_data:
            return

        await self.file.close()

    async def __aenter__(self) -> "AsyncFileReaderWithProgress":
        await self.open()
        return self

    async def __aexit__(self, type, value, traceback) -> None:
        await self.close()

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.current >= self.end:
            raise StopAsyncIteration

        if self.is_owned_data:
            buf = await self.file.read(self.blksize)
        else:
            self.file.seek(self.current)
            buf = self.file.read(self.blksize)
        buf_len = len(buf)

        if self.current + buf_len >= self.end:
            new_buf_len = self.end - self.current
            self.current = self.end
            self.progress and self.progress.update(new_buf_len)
            return buf[:new_buf_len]

        self.progress and self.progress.update(buf_len)
        self.current += buf_len
        return buf

#
# ML expert Platform
# Copyright (c) 2025-present NAVER Cloud Corp.
# Apache-2.0
#

import asyncio
import json
import os
import random
from pathlib import Path
from typing import AsyncIterable, BinaryIO, Callable, Iterable, Optional, Tuple, Union

from httpx import HTTPStatusError, TimeoutException
from rich.console import Console
from rich.filesize import decimal

from .fileio import AsyncFileReaderWithProgress, FileWriterWithProgress
from .progress import Progress, ProgressBar
from .transport_client import TransportClient
from .util import log_call

DEFAULT_MINIMUM_PART_SIZE = 5 * 1024 * 1024  # 5MiB
DEFAULT_MAXIMUM_PART_SIZE = 4 * 1024 * 1024 * 1024  # 4GiB


HEADER_NAME_CONTENT_SHA256 = "x-amz-content-sha256"


def get_sleep_time(retry_count: int, base=1, limit=10) -> float:
    # full jitter
    base_ms = base * 1000
    limit_ms = limit * 1000
    sleep_ms = random.randint(0, min(base_ms * 2**retry_count, limit_ms))
    return sleep_ms / 1000


class TransportApi:
    def __init__(
        self,
        transport_client: TransportClient,
        debug=False,
    ):
        self.transport_client = transport_client
        self.console = Console(log_path=False)
        self.debug = debug

    @staticmethod
    def resource_path_file(
        project_name: str, model_name: str, version: str, remote_path: str
    ) -> str:
        return (
            Path("/")
            / "projects"
            / project_name
            / "models"
            / model_name
            / "versions"
            / version
            / "files"
            / remote_path.lstrip("/")
        ).as_posix()

    @staticmethod
    def calculate_upload_part_size(
        file_size: int,
        parallel_count: int,
        minimum_part_size: int = DEFAULT_MINIMUM_PART_SIZE,
        maximum_part_size: int = DEFAULT_MAXIMUM_PART_SIZE,
    ) -> Tuple[int, int]:
        if minimum_part_size >= maximum_part_size:
            minimum_part_size = maximum_part_size

        minimum_file_size = (parallel_count - 1) ** 2
        if file_size <= minimum_file_size:
            # too small file_size
            return file_size, 1

        if file_size <= minimum_part_size:
            # too small file_size
            return file_size, 1

        part_size = file_size // parallel_count
        if part_size > maximum_part_size:
            part_size = maximum_part_size
        elif part_size < minimum_part_size:
            part_size = minimum_part_size

        part_count = file_size // part_size + (1 if file_size % part_size > 0 else 0)

        return part_size, part_count

    @staticmethod
    def calculate_download_part_size(
        file_size: int,
        parallel_count: int,
        minimum_part_size: int = DEFAULT_MINIMUM_PART_SIZE,
    ) -> Tuple[int, int]:
        if parallel_count < 2:
            # too small parallel_count
            return file_size, 1

        minimum_file_size = (parallel_count - 1) ** 2
        if file_size <= minimum_file_size:
            # too small file_size
            return file_size, 1

        part_size = file_size // parallel_count
        if part_size < minimum_part_size:
            return file_size, 1

        if file_size % parallel_count == 0:
            return part_size, parallel_count
        return part_size + 1, parallel_count

    @log_call
    def download_tasks(
        self,
        resource_path: str,
        output_file: str,
        file_size: int,
        parallel: int,
        progress: Progress,
        use_http: bool,
    ):
        tasks = []
        part_size, parallel_count = self.calculate_download_part_size(
            file_size, parallel
        )
        for worker_index in range(0, parallel_count):
            start = part_size * worker_index
            end = start + part_size
            end = file_size if end > file_size else end

            description = ""
            if parallel_count > 1:
                description = (
                    f"#{worker_index + 1: >{len(str(parallel_count))}}/{parallel_count}"
                )

            data = FileWriterWithProgress(output_file, start, end, progress)
            data.open()
            # if data open in download_part method asynchronously
            # it cause that downloaded file content broken.
            # So, we open all part data of a file here synchronously
            # and the data will be closed in download_part method.

            t = self.download_part(
                resource_path=resource_path,
                output_file=output_file,
                start=start,
                end=end,
                progress=progress,
                description=description,
                data=data,
                force_http=use_http,
            )
            tasks.append(t)
        return tasks

    @log_call
    async def download_part(
        self,
        resource_path: str,
        output_file: str,
        start: int,
        end: int,
        progress: ProgressBar,
        data: BinaryIO,
        description: str = "",
        force_http: bool = False,
    ):
        try:
            assert start <= end
            if start < end:
                headers = {
                    "Range": f"bytes={start}-{end - 1}",
                }
            else:
                headers = {
                    # When size 0,
                    # below code occur server error
                    # (416 Client Error: Requested Range Not Satisfiable)
                    # "Range": f"bytes={start}-",
                }
            size = end - start

            await self.transport_client.get(
                resource_path=resource_path,
                data=data,
                headers=headers,
                force_http=force_http,
            )

            if self.debug:
                progress.log(
                    f"Downloaded part {description}({decimal(size):>9}) - {output_file}",  # noqa: E501
                )
        finally:
            data.close()

    @log_call
    async def download_complete(
        self,
        resource_path: str,
        output_file: str,
        size: int,
        progress: ProgressBar,
        tasks,
        description: str = "",
        complete_callback_func: Optional[Callable[[str, int], None]] = None,
    ):
        await asyncio.gather(*tasks)

        progress.log(f"Downloaded {description}({decimal(size):>9}) - {output_file}")

        if complete_callback_func:
            complete_callback_func(output_file, size)

        if self.debug:
            url = self.transport_client.conf.host + resource_path
            progress.log(
                f"CURL Command Example for download : \n"
                f"\tcurl {url} \\\n"
                f"\t\t-o {output_file} \\\n"
                f'\t\t-H "Authorization: Bearer <access-token>"'
            )

    @log_call
    def upload_tasks(
        self,
        resource_path: str,
        local_file: str,
        overwrite: bool,
        file_size: int,
        part_size: int,
        part_count: int,
        progress: Progress,
        upload_id: asyncio.Future,
        retry: int,
        local_file_sha256: Optional[str] = None,
    ):
        tasks = []

        if file_size == 0:
            t = self.upload_zero_size_file(
                resource_path=resource_path,
                local_file=local_file,
                overwrite=overwrite,
                progress=progress,
                description="",
                retry=retry,
            )
            tasks.append(t)
            return tasks

        for worker_num in range(part_count):
            part_number = worker_num + 1  # part number start from 1 (not 0)
            start = part_size * worker_num
            end = start + part_size
            end = file_size if end > file_size else end

            description = ""
            if part_count > 1:
                description = f"#{part_number: >{len(str(part_count))}}/{part_count}"

            t = self.upload_part(
                resource_path=resource_path,
                local_file=local_file,
                data_source=local_file,
                overwrite=overwrite,
                upload_id=upload_id,
                part_number=part_number,
                start=start,
                end=end,
                progress=progress,
                description=description,
                retry=retry,
                local_file_sha256=local_file_sha256,
            )
            tasks.append(t)

        return tasks

    @log_call
    def upload_fileobj_tasks(
        self,
        resource_path: str,
        fileobj: Tuple[AsyncIterable, Iterable],
        overwrite: bool,
        file_size: int,
        part_size: int,
        part_count: int,
        progress: Progress,
        upload_id: asyncio.Future,
        retry: int,
    ):
        tasks = []

        if file_size == 0:
            t = self.upload_zero_size_file(
                resource_path=resource_path,
                local_file="local-file-obj",
                overwrite=overwrite,
                progress=progress,
                description="",
                retry=retry,
            )
            tasks.append(t)
            return tasks

        for worker_num in range(part_count):
            part_number = worker_num + 1  # part number start from 1 (not 0)
            start = part_size * worker_num
            end = start + part_size
            end = file_size if end > file_size else end

            description = ""
            if part_count > 1:
                description = f"#{part_number: >{len(str(part_count))}}/{part_count}"

            t = self.upload_part(
                resource_path=resource_path,
                local_file="",
                data_source=fileobj,
                overwrite=overwrite,
                upload_id=upload_id,
                part_number=part_number,
                start=start,
                end=end,
                progress=progress,
                description=description,
                retry=retry,
            )
            tasks.append(t)

        return tasks

    @log_call
    async def upload_complete(
        self,
        resource_path: str,
        remote_file: str,
        local_file: str,
        overwrite: bool,
        upload_id: asyncio.Future,
        total_size: int,
        progress: Progress,
        tasks,
        complete_callback_func: Optional[Callable[[str, int], None]] = None,
        local_file_sha256: Optional[str] = None,
    ):
        await asyncio.wait([upload_id])
        await asyncio.gather(*tasks)
        u = upload_id.result()

        if u == "":
            # upload_id is empty when server not support parallel upload
            # Then, we don't need to make the complete post.
            progress.log(f"Uploaded ({decimal(total_size):>9}) - {remote_file}")
            if complete_callback_func:
                complete_callback_func(remote_file, total_size)
            return

        parts_info = []
        for t in tasks:
            res = t.result()
            if "Content-Type" in res.headers and res.headers.get(
                "Content-Type"
            ).startswith("application/json"):
                responseJSON = res.json()
                if "partInfo" in responseJSON:
                    parts_info += [responseJSON["partInfo"]]

        async def parts_data():
            yield json.dumps({"parts": parts_info}, indent=2).encode("utf-8")

        resp = await self.transport_client.post(
            resource_path,
            data=parts_data(),
            headers={
                HEADER_NAME_CONTENT_SHA256: (
                    local_file_sha256 if local_file_sha256 else get_sha256(local_file)
                )
            },
            params={
                "overwrite": overwrite,
                "total-size": total_size,
                "upload-id": u,
            },
        )

        progress.log(f"Uploaded ({decimal(total_size):>9}) - {remote_file}")
        if complete_callback_func:
            complete_callback_func(remote_file, total_size)
        return resp

    @log_call
    async def upload_start(
        self,
        resource_path: str,
        overwrite: bool,
        part_size: int,
        file_size: int,
        progress: Progress,
    ) -> str:
        if part_size == file_size:
            return ""

        try:
            resp = await self.transport_client.post(
                resource_path,
                data=None,
                params={
                    "overwrite": overwrite,
                    "part-size": part_size,
                    "total-size": file_size,
                },
            )
        except HTTPStatusError as e:
            if e.response.status_code == 501:
                # if model registry server not implemented for parallel upload
                # return empty("") upload id for single upload mode
                if self.debug:
                    progress.log(f"server not support parallel upload. {e}")

                return ""
            raise e

        return resp.json()["uploadKey"]

    def data_source_name(self, data_source: Union[str, AsyncIterable, Iterable]) -> str:
        if isinstance(data_source, str):
            return f"{Path(data_source).name}"

        return f"{data_source}"

    @log_call
    async def upload_part(
        self,
        resource_path: str,
        local_file: str,
        data_source: Union[str, AsyncIterable, Iterable],
        start: int,
        end: int,
        overwrite: bool,
        upload_id: asyncio.Future,
        part_number: int,
        progress: ProgressBar,
        description: str = "",
        retry: int = 3,
        local_file_sha256: Optional[str] = None,
    ):
        assert start <= end
        if start == end:
            return

        await asyncio.wait([upload_id])
        u = upload_id.result()

        if u == "":
            if start > 0:
                if self.debug:
                    progress.log(
                        f"Uploaded part {description} Skipped"
                        " - server not support parallel upload"
                    )
                return
            # first file(start == 0) upload whole file on single upload mode
            if isinstance(data_source, str):
                end = os.path.getsize(data_source)
            else:
                end = end

        size = end - start
        headers = {
            "X-Upload-Content-Length": str(size),
        }

        if u == "" and local_file:
            # When u is empty, single upload
            # We need to calculate the sha256 and include it to put submit
            headers[HEADER_NAME_CONTENT_SHA256] = (
                local_file_sha256 if local_file_sha256 else get_sha256(local_file)
            )

        params = {
            "overwrite": overwrite,
            "upload-id": u,
            "part": part_number,
        }

        retry_count = 0
        while True:
            try:
                async with AsyncFileReaderWithProgress(
                    data_source, start, end, progress
                ) as data:
                    response = await self.transport_client.put(
                        resource_path=resource_path,
                        data=data,
                        headers=headers,
                        params=params,
                    )
                break
            except (HTTPStatusError, TimeoutException) as e:
                retry_count += 1
                if retry_count > retry:
                    raise e

                if (
                    isinstance(e, HTTPStatusError)
                    and (e.response.status_code // 100) == 4
                ):
                    raise e

                sleep_sec = get_sleep_time(retry_count)
                await asyncio.sleep(sleep_sec)
                progress.log(
                    f"Retrying({retry_count}/{retry}) to upload part {description} - "
                    f"{self.data_source_name(data_source)}"
                )

        if description and self.debug:
            progress.log(
                f"Uploaded part {description}({decimal(size):>9}) - "
                f"{self.data_source_name(data_source)}"
            )
        return response

    @log_call
    async def upload_zero_size_file(
        self,
        resource_path: str,
        local_file: str,
        overwrite: bool,
        progress: ProgressBar,
        description: str = "",
        retry: int = 3,
    ):
        headers = {
            "X-Upload-Content-Length": "0",
        }

        params = {
            "overwrite": overwrite,
        }

        retry_count = 0
        while True:
            try:
                response = await self.transport_client.put(
                    resource_path=resource_path,
                    data="",
                    headers=headers,
                    params=params,
                )
                break
            except (HTTPStatusError, TimeoutException) as e:
                retry_count += 1
                if retry_count > retry:
                    raise e

                if (
                    isinstance(e, HTTPStatusError)
                    and (e.response.status_code // 100) == 4
                ):
                    raise e

                sleep_sec = get_sleep_time(retry_count)
                await asyncio.sleep(sleep_sec)
                progress.log(
                    f"Retrying({retry_count}/{retry}) to upload part {description} - "
                    f"{Path(local_file).name}"
                )

        if description and self.debug:
            progress.log(f"Uploaded zero file {description} - {Path(local_file).name}")
        return response


@log_call
def get_sha256(path: str) -> str:
    import hashlib
    import sys

    if sys.version_info >= (3, 11):
        with open(path, "rb") as f:
            digest = hashlib.file_digest(f, "sha256")
    else:
        digest = hashlib.sha256()
        with open(path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                digest.update(byte_block)

    return digest.hexdigest()

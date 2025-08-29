#
# ML expert Platform
# Copyright (c) 2025-present NAVER Cloud Corp.
# Apache-2.0
#

import asyncio
import datetime
import fnmatch
import os
import re
from io import IOBase
from pathlib import Path
from typing import Callable, Iterator, List, Optional, Tuple, Union, cast

import requests
from pydantic import BaseModel, Field

from mlx.api.model_registry import (
    ApiClient,
    Configuration,
    File,
    FilesResponse,
    HealthResponse,
    Model,
    ModelRequest,
    ModelsResponse,
    ModelUpdateRequest,
    Version,
    VersionRequest,
    VersionsResponse,
    VersionUpdateRequest,
)
from mlx.api.model_registry import FilesApi as OriginFilesApi
from mlx.api.model_registry import HealthApi as OriginHealthApi
from mlx.api.model_registry import ModelsApi as OriginModelApi
from mlx.api.model_registry import PublicApi as OriginPublicApi
from mlx.api.model_registry import VersionsApi as OriginModelVersionApi
from mlx.api.model_registry.rest import ApiException

from . import filewalker, hmac_auth
from .file_comp import FileCompList
from .progress import ProgressBar
from .task_pool import TaskPool
from .transport_api import TransportApi, TransportClient, get_sha256
from .user_agent import USER_AGENT
from .util import log_call, model_uri, proxy_url


class HealthApi:
    """HealthAPI."""

    def __init__(self, api_client: ApiClient, debug=False):
        """Initializer of HealthAPI

        Args:
            api_client (ApiClient): api_client
            debug (bool): debug flag
        """
        self.api = OriginHealthApi(api_client)
        self.debug = debug

    @log_call
    def check(self) -> HealthResponse:
        """check health status

        Returns:
            HealthResponse:
        """
        return cast(
            HealthResponse,
            self.api.get_health(),
        )


class ModelAPI:
    """ModelAPI."""

    def __init__(self, api_client: ApiClient, debug=False):
        """Initializer of ModelAPI

        Args:
            api_client (ApiClient): api_client
            debug (bool): debug flag
        """
        self.api = OriginModelApi(api_client)
        self.debug = debug

    @log_call
    def create(self, project_name: str, model: ModelRequest) -> Model:
        """create.

        Args:
            project_name (str): project_name
            model (ModelRequest): model

        Returns:
            Model:
        """
        return cast(
            Model,
            self.api.create_model(
                project_name=project_name,
                model_request=model,
            ),
        )

    @log_call
    def get(self, project_name: str, model_name: str) -> Model:
        """get.

        Args:
            project_name (str): project_name
            model_name (str): model_name

        Returns:
            Model:
        """

        return cast(
            Model,
            self.api.get_model(
                project_name=project_name,
                model_name=model_name,
            ),
        )

    @log_call
    def exist(self, project_name: str, model_name: str) -> bool:
        """exist.

        Args:
            project_name (str): project_name
            model_name (str): model_name

        Returns:
            bool: True if exist, False if server return http status 404,
                  or raise exception
        """

        try:
            _ = self.get(project_name, model_name)
            return True
        except ApiException as e:
            if e.status == 404:
                return False
            raise e

    @log_call
    def update(
        self,
        project_name: str,
        model_name: str,
        model: ModelUpdateRequest,
    ) -> Model:
        """update.

        Args:
            project_name (str): project_name
            model_name (str): model_name
            model (ModelUpdateRequest): model

        Returns:
            Model:
        """
        return cast(
            Model,
            self.api.update_model(
                project_name=project_name,
                model_name=model_name,
                model_update_request=model,
            ),
        )

    @log_call
    def delete(self, project_name: str, model_name: str) -> None:
        """delete.

        Args:
            project_name (str): project_name
            model_name (str): model_name

        Returns:
            None:
        """
        return cast(
            None,
            self.api.delete_model(
                project_name=project_name,
                model_name=model_name,
            ),
        )

    @log_call
    def list(
        self,
        project_name: str,
        page=0,
        page_size=30,
        sort_by="",
        ascending=False,
        search="",
        tags=[],
    ) -> ModelsResponse:
        """list.

        Args:
            project_name (str): project_name
            page (int): Page index for pagination (default: 0)
            page_size (int): Page size for pagination (default: 30)
            sort_by (str): Field to sort results on (default: "")
            search (str): Search query string (default: "")
            ascending (bool): Sorts by ascending values if set to true,
                              default is descending  (default: False)
            tags (List[str]): Tags to filter model results on (default: [])

        Returns:
            ModelsResponse:
        """
        return cast(
            ModelsResponse,
            self.api.get_models(
                project_name=project_name,
                page=page,
                page_size=page_size,
                sort_by=sort_by,
                ascending=ascending,
                search=search,
                tags=tags,
            ),
        )


class ModelVersionAPI:
    """ModelVersionAPI."""

    def __init__(self, api_client: ApiClient, debug=False):
        """__init__.

        Args:
            api_client (ApiClient): api_client
            debug (bool): debug flag
        """
        self.debug = debug
        self.api = OriginModelVersionApi(api_client)

    @log_call
    def create(
        self,
        project_name: str,
        model_name: str,
        version: VersionRequest,
    ) -> Version:
        """create.

        Args:
            project_name (str): project_name
            model_name (str): model_name
            version (VersionRequest): version

        Returns:
            Version:
        """
        return cast(
            Version,
            self.api.create_version(
                project_name=project_name,
                model_name=model_name,
                version_request=version,
            ),
        )

    @log_call
    def get(
        self,
        project_name: str,
        model_name: str,
        version_name: str,
    ) -> Version:
        """get.

        Args:
            project_name (str): project_name
            model_name (str): model_name
            version_name (str): version_name

        Returns:
            Version:
        """
        return cast(
            Version,
            self.api.get_version(
                project_name=project_name,
                model_name=model_name,
                version_name=version_name,
            ),
        )

    @log_call
    def exist(self, project_name: str, model_name: str, version_name: str) -> bool:
        """exist.

        Args:
            project_name (str): project_name
            model_name (str): model_name
            version_name (str): version_name

        Returns:
            bool: True if exist, False if server return http status 404,
                  or raise exception
        """

        try:
            _ = self.get(project_name, model_name, version_name)
            return True
        except ApiException as e:
            if e.status == 404:
                return False
            raise e

    @log_call
    def update(
        self,
        project_name: str,
        model_name: str,
        version_name: str,
        version: VersionUpdateRequest,
    ) -> Version:
        """update.

        Args:
            project_name (str): project_name
            model_name (str): model_name
            version_name (str): version_name
            version (VersionUpdateRequest): version

        Returns:
            Version:
        """
        return cast(
            Version,
            self.api.update_version(  # noqa: E501
                project_name=project_name,
                model_name=model_name,
                version_name=version_name,
                version_update_request=version,
            ),
        )

    @log_call
    def delete(
        self,
        project_name: str,
        model_name: str,
        version_name: str,
    ) -> None:
        """delete.

        Args:
            project_name (str): project_name
            model_name (str): model_name
            version_name (str): version_name

        Returns:
            None:
        """
        return cast(
            None,
            self.api.delete_version(  # noqa: E501
                project_name=project_name,
                model_name=model_name,
                version_name=version_name,
            ),
        )

    @log_call
    def list(
        self,
        project_name: str,
        model_name: str,
        page=0,
        page_size=30,
        sort_by="",
        ascending=False,
        search="",
        tags=[],
    ) -> VersionsResponse:
        """list.

        Args:
            project_name (str): project_name
            model_name (str): model_name
            page (int): Page index for pagination (default: 0)
            page_size (int): Page size for pagination (default: 30)
            sort_by (str): Field to sort results on (default: "")
            search (str): Search query string (default: "")
            ascending (bool): Sorts by ascending values if set to true,
                              default is descending (default: False)
            tags (List[str]): Tags to filter model results on (default: [])

        Returns:
            VersionsResponse:
        """
        return cast(
            VersionsResponse,
            self.api.get_versions(
                project_name=project_name,
                model_name=model_name,
                page=page,
                page_size=page_size,
                ascending=ascending,
                sort_by=sort_by,
                search=search,
                tags=tags,
            ),
        )

    @log_call
    def uri(
        self,
        project_name: str,
        model_name: str,
        version_name: str,
    ) -> str:
        """uri.

        Args:
            project_name (str): project_name
            model_name (str): model_name
            version_name (str): version_name

        Returns:
            str: uri string
        """
        url_format = re.compile(r"https?://")
        endpoint = (
            url_format.sub(
                "",
                self.api.api_client.configuration.host,
            )
            .strip()
            .strip("/")
        )

        return model_uri(endpoint, project_name, model_name, version_name)


class FileComp(BaseModel):
    """
    file comparison record class
    """

    same: bool = Field(description="sameness status of a file")
    local_path: str = Field("", description="local file path")
    local_size: int = Field(0, description="local file size")
    local_last_updated: Optional[datetime.datetime] = Field(
        description="local file last updated time",
        default=None,
    )
    remote_path: str = Field("", description="remote file path")
    remote_size: int = Field(0, description="remote file size")
    remote_only: bool = Field(False, description="True if no local file exists")
    remote_last_updated: Optional[datetime.datetime] = Field(
        description="remote file last updated time",
        default=None,
    )


class Verification(BaseModel):
    """
    verification result data class
    """

    same: bool = Field(description="sameness status of file set")
    files: List[FileComp] = Field([], description="list of FileComp")


class FileAPI:
    """FileAPI."""

    def __init__(self, api_client: ApiClient, access_token: str, debug=False):
        """__init__.

        Args:
            api_client (ApiClient): api_client
            debug (bool): debug flag
        """
        self.access_token = access_token
        self.debug = debug
        self.api_client = api_client
        self.file_api = OriginFilesApi(api_client)
        self.transport_client = TransportClient(api_client.configuration)
        self.transport_api = TransportApi(
            transport_client=self.transport_client,
            debug=self.debug,
        )

    @log_call
    def upload_sync(
        self,
        project_name: str,
        model_name: str,
        version_name: str,
        local_path: str,
        remote_path: str,
        includes: List[str] = [],
        excludes: List[str] = [],
        overwrite=False,
        parallel=1,
        timeout: int = None,
        retry=3,
        dry_run=False,
        progress_callback_func: Optional[Callable[[int, int], None]] = None,
        file_complete_callback_func: Optional[Callable[[str, int], None]] = None,
        skip_if_exist=False,
    ) -> None:
        """upload api for SYNC

        Examples:
            Uploading a model file set.
            ```python
            from mlx.sdk.model_registry import *

            API_ENDPOINT = "<model-registry-endpoint>"
            ACCESS_TOKEN = "<access-token>"
            PROJECT_NAME = "<your-project-name>"
            MODEL_NAME = "<your-model-name>"
            VERSION_NAME = "<your-version-name>"

            api = ModelRegistryAPI(API_ENDPOINT, ACCESS_TOKEN)
            file_api = api.file_api

            # Upload local model files with callback function for progress, file completion
            def progress_callback(progress_size: int, total_size: int):
                print(progress_size, total_size)

            def completion_callback(file_path: str, size: int):
                print(file_path, size)

            file_api.upload_sync(
                project_name=PROJECT_NAME,
                model_name=MODEL_NAME,
                version_name=VERSION_NAME,
                local_path=LOCAL_MODEL_DIRECTORY,
                remote_path="/",
                excludes=[],
                overwrite=True,
                parallel=1,
                progress_callback_func=progress_callback,
                file_complete_callback_func=completion_callback,
            )
            ```

        Args:
            project_name (str): project_name
            model_name (str): model_name
            version_name (str): version_name
            local_path (str): local_path
            remote_path (str): remote_path
            includes (List[str]): includes
            excludes (List[str]): excludes
            overwrite (bool): overwrite flag
            parallel (int): number of parallel
            timeout (int): int number of seconds to wait for. if None, no timeout
            retry (int): int number of seconds to retry upload.
            dry_run (bool): dry run flag
            progress_callback_func (Optional[Callable[[int, int], None]]):
                callback function for upload progress with (progress_size, total_size)
                in bytes
            file_complete_callback_func (Optional[Callable[[str, int], None]]):
                callback function for file completion event
                with (file path, file size in bytes)
            skip_if_exist (bool): skip upload if same file exist

        Returns:
            None:

        """
        task = self.upload(
            project_name=project_name,
            model_name=model_name,
            version_name=version_name,
            local_path=local_path,
            remote_path=remote_path,
            includes=includes,
            excludes=excludes,
            overwrite=overwrite,
            parallel=parallel,
            retry=retry,
            dry_run=dry_run,
            progress_callback_func=progress_callback_func,
            file_complete_callback_func=file_complete_callback_func,
            skip_if_exist=skip_if_exist,
        )

        asyncio.run(asyncio.wait_for(task, timeout=timeout))

    @log_call
    async def upload(
        self,
        project_name: str,
        model_name: str,
        version_name: str,
        local_path: str,
        remote_path: str,
        includes: List[str] = [],
        excludes: List[str] = [],
        overwrite=False,
        parallel=1,
        retry=3,
        dry_run=False,
        progress_callback_func: Optional[Callable[[int, int], None]] = None,
        file_complete_callback_func: Optional[Callable[[str, int], None]] = None,
        skip_if_exist=False,
    ) -> None:
        """upload api for ASYNC. it returns a coroutine that must be awaited.

        Args:
            project_name (str): project_name
            model_name (str): model_name
            version_name (str): version_name
            local_path (str): local_path
            remote_path (str): remote_path
            includes (List[str]): includes
            excludes (List[str]): excludes
            overwrite (bool): overwrite flag
            parallel (int): number of parallel
            retry (int): number to retry when upload is failed
            dry_run (bool): dry run flag
            progress_callback_func (Optional[Callable[[int, int], None]]):
                callback function for upload progress with (progress_size, total_size)
                in bytes
            file_complete_callback_func (Optional[Callable[[str, int], None]]):
                callback function for file completion event
                with (file path, file size in bytes)
            skip_if_exist (bool): skip upload if same file exist

        Returns:
            None:
        """

        if dry_run:
            self._dry_run_upload(
                project_name=project_name,
                model_name=model_name,
                version_name=version_name,
                local_path=local_path,
                remote_path=remote_path,
                overwrite=overwrite,
                includes=includes,
                excludes=excludes,
            )
            return

        total_size = 0
        for local_file, remote_file in filewalker.walk(local_path, remote_path):
            if not self.is_target(local_file, includes, excludes, root_path=local_path):
                continue
            total_size += Path(local_file).stat().st_size

        remote_files = {}
        if skip_if_exist:
            for r, _, file in self._list_download_items(
                project_name=project_name,
                model_name=model_name,
                version_name=version_name,
                remote_path=remote_path,
                local_path=local_path,
            ):
                remote_files[r] = file

        start = datetime.datetime.now()

        progressbar = ProgressBar(
            "[bold blue]Uploading", progress_callback_func, self.debug
        )
        progressbar.total(total_size)

        await self.transport_client.open()

        pool = TaskPool(parallel, self.debug)
        for local_file, remote_file in filewalker.walk(local_path, remote_path):
            if not self.is_target(local_file, includes, excludes, root_path=local_path):
                continue

            file_size = os.path.getsize(local_file)
            remote_file_info = remote_files.get(remote_file, None)
            local_file_sha256 = get_sha256(local_file)
            if skip_if_exist and remote_file_info:
                if remote_file_info.sha256 == local_file_sha256:
                    progressbar.log(f"SKIPED exist file : {remote_file}")
                    progressbar.update(file_size)
                    continue

            part_size, part_count = TransportApi.calculate_upload_part_size(
                file_size, parallel
            )

            resource_path = TransportApi.resource_path_file(
                project_name,
                model_name,
                version_name,
                remote_file,
            )
            upload_start = self.transport_api.upload_start(
                resource_path=resource_path,
                overwrite=overwrite,
                part_size=part_size,
                file_size=file_size,
                progress=progressbar,
            )

            upload_id = await pool.submit(upload_start)

            upload_part_tasks = []
            for task in self.transport_api.upload_tasks(
                resource_path=resource_path,
                local_file=local_file,
                overwrite=overwrite,
                file_size=file_size,
                part_size=part_size,
                part_count=part_count,
                progress=progressbar,
                upload_id=upload_id,
                retry=retry,
                local_file_sha256=local_file_sha256,
            ):
                t = await pool.submit(task)
                upload_part_tasks.append(t)

            upload_complete = self.transport_api.upload_complete(
                resource_path=resource_path,
                remote_file=remote_file,
                local_file=local_file,
                overwrite=overwrite,
                upload_id=upload_id,
                total_size=file_size,
                progress=progressbar,
                tasks=upload_part_tasks,
                complete_callback_func=file_complete_callback_func,
                local_file_sha256=local_file_sha256,
            )

            await pool.submit(upload_complete)

        await pool.join()
        progressbar.close("[bold green]Complete!")
        await self.transport_client.close()

        self._finalize_upload(
            project_name=project_name,
            model_name=model_name,
            version_name=version_name,
            local_path=local_path,
            remote_path=remote_path,
            upload_start=start,
        )

    @log_call
    async def upload_fileobj(
        self,
        project_name: str,
        model_name: str,
        version_name: str,
        fileobj: IOBase,
        size: int,
        remote_file: str,
        overwrite=False,
        parallel=1,
        retry=3,
    ) -> None:
        """upload_fileobj api for ASYNC. it returns a coroutine that must be awaited.

        Args:
            project_name (str): project_name
            model_name (str): model_name
            version_name (str): version_name
            fileobj (IOBase): file-like object
            size (int): size of fileobj
            remote_file (str): remote file path
            overwrite (bool): overwrite flag
            retry (int): number to retry when upload is failed

        Returns:
            None:
        """

        if not hasattr(fileobj, "read"):
            raise ValueError("fileobj must implement read")

        total_size = size
        start = datetime.datetime.now()

        progressbar = ProgressBar(
            "[bold blue]Uploading from file object", debug=self.debug
        )
        progressbar.total(total_size)

        await self.transport_client.open()

        pool = TaskPool(parallel, self.debug)

        file_size = size
        part_size, part_count = TransportApi.calculate_upload_part_size(
            file_size,
            parallel,
        )

        resource_path = TransportApi.resource_path_file(
            project_name,
            model_name,
            version_name,
            remote_file,
        )
        upload_start = self.transport_api.upload_start(
            resource_path=resource_path,
            overwrite=overwrite,
            part_size=part_size,
            file_size=file_size,
            progress=progressbar,
        )

        upload_id = await pool.submit(upload_start)

        upload_part_tasks = []
        for task in self.transport_api.upload_fileobj_tasks(
            resource_path=resource_path,
            fileobj=fileobj,
            overwrite=overwrite,
            file_size=file_size,
            part_size=part_size,
            part_count=part_count,
            progress=progressbar,
            upload_id=upload_id,
            retry=retry,
        ):
            t = await pool.submit(task)
            upload_part_tasks.append(t)

        upload_complete = self.transport_api.upload_complete(
            resource_path=resource_path,
            remote_file=remote_file,
            local_file="",
            overwrite=overwrite,
            upload_id=upload_id,
            total_size=file_size,
            progress=progressbar,
            tasks=upload_part_tasks,
        )

        await pool.submit(upload_complete)

        await pool.join()
        progressbar.close("[bold green]Complete!")
        await self.transport_client.close()

        self._finalize_upload(
            project_name=project_name,
            model_name=model_name,
            version_name=version_name,
            local_path=f"{fileobj}",
            remote_path=remote_file,
            upload_start=start,
        )

    @log_call
    def _dry_run_upload(
        self,
        project_name: str,
        model_name: str,
        version_name: str,
        local_path: str,
        remote_path: str,
        includes: List[str] = [],
        excludes: List[str] = [],
        overwrite=False,
    ):
        try:
            remote_file_set = set(
                [
                    remote_file
                    for remote_file, _, _ in self._list_download_items(
                        project_name=project_name,
                        model_name=model_name,
                        version_name=version_name,
                        remote_path=remote_path,
                        local_path=local_path,
                    )
                ]
            )
        except ApiException as e:
            if e.reason == "Not Found":
                remote_file_set = set()
            else:
                raise e

        already_exist_list = []
        lpath_max_len = 0
        for local_file, _ in filewalker.walk(local_path, remote_path):
            if lpath_max_len < len(local_file):
                lpath_max_len = len(local_file)

        print(f"{'STATUS':<12}   {'LOCAL PATH':<{lpath_max_len}} => REMOTE PATH")
        for local_file, remote_file in filewalker.walk(local_path, remote_path):
            result = "OK"
            output_path = ""
            detail_info = ""
            if not self.is_target(local_file, includes, excludes, root_path=local_path):
                result = "SKIP"
            elif remote_file in remote_file_set:
                if overwrite:
                    detail_info = "(OVERWRITE)"
                    output_path = remote_file
                else:
                    result = "ERROR"
                    detail_info = "(FILE ALREADY EXIST)"
                    output_path = remote_file
                    already_exist_list.append(remote_file)
            else:
                output_path = remote_file

            print(
                f"{result:<12} : {local_file:<{lpath_max_len}} => {detail_info}{output_path}"  # noqa: E501
            )

        if already_exist_list:
            raise FileExistsError(f"remote file exists already = {already_exist_list}")

    @log_call
    def verify_upload(
        self,
        project_name: str,
        model_name: str,
        version_name: str,
        local_path: str,
        remote_path: str,
        includes: List[str] = [],
        excludes: List[str] = [],
        overwrite=False,
    ) -> Tuple[bool, FileCompList]:
        fcl = FileCompList()
        try:
            for remote_file, _, file_info in self._list_download_items(
                project_name=project_name,
                model_name=model_name,
                version_name=version_name,
                remote_path=remote_path,
                local_path=local_path,
            ):
                fcl.add_file_remote_info(
                    remote_file, file_info.size, file_info.last_updated
                )

        except ApiException as e:
            if e.reason == "Not Found":
                pass  # empty OK
            else:
                raise e

        for local_file, remote_file, file_info in self._list_local_items(
            local_path,
            remote_path,
        ):
            if not self.is_target(local_file, includes, excludes, root_path=local_path):
                continue
            fcl.add_file_local_info(
                local_file,
                remote_file,
                Path(local_file).stat().st_size,
                Path(local_file).stat().st_mtime,
            )

        if fcl.exist_local_only() or fcl.is_diff():
            return (False, fcl)
        return (True, fcl)

    @log_call
    def verify_download(
        self,
        project_name: str,
        model_name: str,
        version_name: str,
        remote_path: str,
        local_path: str,
        includes: List[str] = [],
        excludes: List[str] = [],
    ) -> Tuple[bool, FileCompList]:
        fcl = FileCompList()
        try:
            for remote_file, _, file_info in self._list_download_items(
                project_name=project_name,
                model_name=model_name,
                version_name=version_name,
                remote_path=remote_path,
                local_path=local_path,
            ):
                if not self.is_target(
                    remote_file, includes, excludes, root_path=local_path
                ):
                    continue

                fcl.add_file_remote_info(
                    remote_file, file_info.size, file_info.last_updated
                )

        except ApiException as e:
            if e.reason == "Not Found":
                pass  # no item
            else:
                raise e

        for local_file, remote_file, file_info in self._list_local_items(
            local_path,
            remote_path,
        ):
            fcl.add_file_local_info(
                local_file,
                f"/{remote_file}",
                Path(local_file).stat().st_size,
                Path(local_file).stat().st_mtime,
            )

        if fcl.exist_remote_only() or fcl.is_diff():
            return (False, fcl)
        return (True, fcl)

    @log_call
    def download_sync(
        self,
        project_name: str,
        model_name: str,
        version_name: str,
        remote_path: str,
        local_path: str,
        overwrite=False,
        parallel=1,
        timeout: int = None,
        includes: List[str] = [],
        excludes: List[str] = [],
        dry_run=False,
        use_http=False,
        progress_callback_func: Optional[Callable[[int, int], None]] = None,
        file_complete_callback_func: Optional[Callable[[str, int], None]] = None,
        skip_if_exist=False,
    ) -> None:
        """download api for SYNC

        Examples:
            Downloading a model file set.
            ```python
            from mlx.sdk.model_registry import *

            API_ENDPOINT = "<model-regsitry-endpoint>"
            ACCESS_TOKEN = "<access-token>"
            PROJECT_NAME = "<your-project-name>"
            MODEL_NAME = "<your-model-name>"
            VERSION_NAME = "<your-version-name>"

            api = ModelRegistryAPI(API_ENDPOINT, ACCESS_TOKEN)
            file_api = api.file_api


            # Download model files with callback function for progress, file completion
            def progress_callback(progress_size: int, total_size: int):
                print(progress_size, total_size)


            def completion_callback(file_path: str, size: int):
                print(file_path, size)


            file_api.download_sync(
                project_name=PROJECT_NAME,
                model_name=MODEL_NAME,
                version_name=VERSION_NAME,
                remote_path="/",
                local_path="./temp",
                overwrite=True,
                parallel=1,
                progress_callback_func=progress_callback,
                file_complete_callback_func=completion_callback,
            )
            ```

        Args:
            project_name (str): project_name
            model_name (str): model_name
            version_name (str): version_name
            remote_path (str): remote_path
            local_path (str): local_path
            overwrite (bool): overwrite flag
            parallel (int): number of parallel
            timeout (int): timeout
            includes (List[str]): includes
            excludes (List[str]): excludes
            dry_run (bool): dry run flag
            progress_callback_func (Optional[Callable[[int, int], None]]):
                callback function for download progress
                with (progress_size, total_size) in bytes
            file_complete_callback_func (Optional[Callable[[str, int], None]]):
                callback function for file completion event
                with (file path, file size in bytes)
            skip_if_exist (bool): skip download if same file exist

        Returns:
            None:
        """

        task = self.download(
            project_name=project_name,
            model_name=model_name,
            version_name=version_name,
            remote_path=remote_path,
            local_path=local_path,
            overwrite=overwrite,
            parallel=parallel,
            includes=includes,
            excludes=excludes,
            dry_run=dry_run,
            use_http=use_http,
            progress_callback_func=progress_callback_func,
            file_complete_callback_func=file_complete_callback_func,
            skip_if_exist=skip_if_exist,
        )

        asyncio.run(asyncio.wait_for(task, timeout=timeout))

    @log_call
    def is_target(
        self,
        target_path: str,
        includes: List[str],
        excludes: List[str],
        root_path: str = "/",
    ) -> bool:
        path_without_root = target_path.lstrip(root_path)

        if includes:
            found = False
            for i in includes:
                if i == target_path or fnmatch.fnmatch(target_path, i):
                    found = True
                    break
                if i == path_without_root or fnmatch.fnmatch(path_without_root, i):
                    found = True
                    break
            if not found:
                # Explicit Include, but Not Found
                if self.debug:
                    print(f"SKIPPED : {target_path} by include patterns({includes}) ")
                return False

        if excludes:
            found = False
            for e in excludes:
                if e == target_path or fnmatch.fnmatch(target_path, e):
                    found = True
                    break
                if e == path_without_root or fnmatch.fnmatch(path_without_root, e):
                    found = True
                    break
            if found:
                # Explicit Exclude
                if self.debug:
                    print(f"SKIPPED : {target_path} by excludes patterns({excludes}) ")
                return False

        return True

    @log_call
    async def download(
        self,
        project_name: str,
        model_name: str,
        version_name: str,
        remote_path: str,
        local_path: str,
        overwrite=False,
        parallel=1,
        includes: List[str] = [],
        excludes: List[str] = [],
        dry_run=False,
        use_http=False,
        progress_callback_func: Optional[Callable[[int, int], None]] = None,
        file_complete_callback_func: Optional[Callable[[str, int], None]] = None,
        skip_if_exist=False,
    ) -> None:
        """download api for ASYNC. it returns a coroutine that must be awaited.

        Args:
            project_name (str): project_name
            model_name (str): model_name
            version_name (str): version_name
            remote_path (str): remote_path
            local_path (str): local_path
            overwrite (bool): overwrite flag
            parallel (int) : number of parallel
            includes (List[str]): includes
            excludes (List[str]): excludes
            dry_run (bool): dry run flag
            progress_callback_func (Optional[Callable[[int, int], None]]):
                callback function for download progress with (progress_size, total_size)
                in bytes
            file_complete_callback_func (Optional[Callable[[str, int], None]]):
                callback function for file completion event
                with (file path, file size in bytes)

        Returns:
            None:
        """

        if dry_run:
            self._dry_run_download(
                project_name=project_name,
                model_name=model_name,
                version_name=version_name,
                remote_path=remote_path,
                local_path=local_path,
                overwrite=overwrite,
                includes=includes,
                excludes=excludes,
            )
            return

        total_size = 0
        for rpath, lpath, file_info in self._list_download_items(
            project_name, model_name, version_name, remote_path, local_path
        ):
            if not self.is_target(rpath, includes, excludes):
                continue

            if file_info.size:
                total_size += file_info.size

            if not overwrite and os.path.exists(lpath):
                raise FileExistsError(f"local file exists already = {lpath}")

        progressbar = ProgressBar(
            "[bold blue]Downloading", progress_callback_func, self.debug
        )
        progressbar.total(total_size)

        await self.transport_client.open()

        pool = TaskPool(parallel, self.debug)
        for rfile, lfile, file_info in self._list_download_items(
            project_name, model_name, version_name, remote_path, local_path
        ):
            if not self.is_target(rfile, includes, excludes):
                continue

            if skip_if_exist and os.path.exists(lfile) and file_info.sha256:
                if file_info.sha256 == get_sha256(lfile):
                    progressbar.log(f"SKIPED exist file : {lfile}")
                    progressbar.update(file_info.size)
                    continue

            base_dir = os.path.dirname(lfile)
            if base_dir and not os.path.exists(base_dir):
                os.makedirs(base_dir)

            resource_path = TransportApi.resource_path_file(
                project_name,
                model_name,
                version_name,
                rfile,
            )
            download_part_tasks = []
            for task in self.transport_api.download_tasks(
                resource_path=resource_path,
                output_file=lfile,
                file_size=file_info.size,
                parallel=parallel,
                progress=progressbar,
                use_http=use_http,
            ):
                t = await pool.submit(task)
                download_part_tasks.append(t)

            download_complete_task = self.transport_api.download_complete(
                resource_path=resource_path,
                output_file=lfile,
                size=file_info.size,
                tasks=download_part_tasks,
                progress=progressbar,
                complete_callback_func=file_complete_callback_func,
            )
            await pool.submit(download_complete_task)

        await pool.join()

        await self.transport_client.close()

        progressbar.close("[bold green]Complete!")

        self._increase_download_count(project_name, model_name, version_name)

    def _increase_download_count(
        self,
        project_name: str,
        model_name: str,
        version_name: str,
    ) -> None:
        """increase_download_count.
        Since the api is hidden from swagger doc, call api directly.

        Args:
            project_name (str): project_name
            model_name (str): model_name
            version_name (str): version_name

        Returns:
            None:
        """
        host = self.api_client.configuration.host.rstrip("/")
        path = f"/private/projects/{project_name}/models/{model_name}/versions/{version_name}/download-count"  # noqa : E501

        try:
            requests.get(
                f"{host}{path}",
                auth=hmac_auth.HmacAuth(),
                headers={"Authorization": f"Bearer {self.access_token}"},
                verify=self.api_client.configuration.verify_ssl,
            )

        except Exception:
            # ignore error for download-count
            pass

    def _finalize_upload(
        self,
        project_name: str,
        model_name: str,
        version_name: str,
        local_path: str,
        remote_path: str,
        upload_start: datetime.datetime,
    ) -> None:
        """_finalize_upload.
        Tells the model registry to run post-upload operations.
        Since the api is hidden from swagger doc, call api directly.

        Args:
            project_name (str): project_name
            model_name (str): model_name
            version_name (str): version_name

        Returns:
            None:
        """
        host = self.api_client.configuration.host.rstrip("/")
        path = f"/private/projects/{project_name}/models/{model_name}/versions/{version_name}/finalize-upload"  # noqa : E501

        f = Path(local_path)
        is_dir = f.is_dir()

        local_path = local_path.rstrip("/")
        remote_path = remote_path.rstrip("/")

        # If remote path was not specified it will be the same as the local path
        if remote_path == "":
            remote_path = os.path.basename(local_path)

        # Data object is not part of swagger doc - so construct it manually
        data = {
            "localPath": local_path,
            "remotePath": remote_path,
            "dir": is_dir,
            "uploadStart": upload_start.astimezone().isoformat(),
            "uri": model_uri(host, project_name, model_name, version_name),
        }

        try:
            resp = requests.post(
                f"{host}{path}",
                json=data,
                headers={"Authorization": f"Bearer {self.access_token}"},
                verify=self.api_client.configuration.verify_ssl,
            )
            if resp.status_code != 200:
                raise Exception(f"unexpected error code {resp.status_code}")
        except Exception as e:
            # allow error for finalizing upload
            print(f"Error running post-upload functions: {e}")

    def _dry_run_download(
        self,
        project_name: str,
        model_name: str,
        version_name: str,
        remote_path: str,
        local_path: str,
        overwrite=False,
        includes: List[str] = [],
        excludes: List[str] = [],
    ) -> None:
        already_exist_list = []
        rpath_max_len = 0
        for rpath, _, _ in self._list_download_items(
            project_name, model_name, version_name, remote_path, local_path
        ):
            if rpath_max_len < len(rpath):
                rpath_max_len = len(rpath)

        print(f"{'STATUS':<12}   {'REMOTE PATH':<{rpath_max_len}} => LOCAL PATH")
        for rpath, lpath, _ in self._list_download_items(
            project_name, model_name, version_name, remote_path, local_path
        ):
            result = "OK"
            output_path = ""
            detail_info = ""
            if not self.is_target(rpath, includes, excludes):
                result = "SKIP"
            elif os.path.exists(lpath):
                if overwrite:
                    detail_info = "(OVERWRITE)"
                    output_path = lpath
                else:
                    result = "ERROR"
                    detail_info = "(FILE ALREADY EXIST)"
                    output_path = lpath
                    already_exist_list.append(lpath)
            else:
                output_path = lpath

            print(
                f"{result:<12} : {rpath:<{rpath_max_len}} => {detail_info}{output_path}"
            )

        if already_exist_list:
            raise FileExistsError(f"local file exists already = {already_exist_list}")

    @log_call
    def verify(
        self,
        project_name: str,
        model_name: str,
        version_name: str,
        local_path: str,
        time_compare: bool = True,
    ) -> Verification:
        """verify downloaded model files

        Args:
            project_name (str): project_name
            model_name (str): model_name
            version_name (str): version_name
            local_path (str): local_path
            time_compare (bool): if set True, verification failed
                                 when local file older than remote file

        Returns:
            Verification:
        """

        _, file_comp_list = self.verify_download(
            project_name,
            model_name,
            version_name,
            "",
            local_path,
        )

        ret = Verification(same=True)
        for lfile, lfile_info, rfile, rfile_info in file_comp_list.each():
            if not lfile:
                ret.files.append(
                    FileComp(
                        same=False,
                        remote_path=rfile,
                        remote_size=rfile_info.size,
                        remote_only=True,
                        remote_last_updated=rfile_info.last_updated,
                    )
                )
                ret.same = False
                continue

            if not rfile:
                # skip local only file info
                continue

            file = FileComp(
                same=True,
                local_path=lfile,
                local_size=lfile_info.size,
                local_last_updated=lfile_info.last_updated,
                remote_path=rfile,
                remote_size=rfile_info.size,
                remote_last_updated=rfile_info.last_updated,
            )

            if lfile_info.size != rfile_info.size:
                file.same = False
                ret.same = False

            if (
                time_compare
                and lfile_info.last_updated
                and rfile_info.last_updated
                and (rfile_info.last_updated > lfile_info.last_updated)
            ):
                file.same = False
                ret.same = False

            ret.files.append(file)

        return ret

    @log_call
    def delete(
        self,
        project_name: str,
        model_name: str,
        version_name: str,
        file_name: str,
    ) -> None:
        """delete.

        Args:
            project_name (str): project_name
            model_name (str): model_name
            version_name (str): version_name
            file_name (str): file_name

        Returns:
            None:
        """
        return cast(
            None,
            self.file_api.delete_file(  # noqa: E501
                project_name=project_name,
                model_name=model_name,
                version_name=version_name,
                file_name=file_name,
            ),
        )

    @log_call
    def list(
        self,
        project_name: str,
        model_name: str,
        version_name: str,
        dir: str = "/",
        recursive: bool = False,
    ) -> Union[FilesResponse, Iterator[Tuple[str, File]]]:
        """list.

        Args:
            project_name (str): project_name
            model_name (str): model_name
            version_name (str): version_name
            dir (str): dir
            recursive (bool): recursive
                if set False, just return FilesResponse instance for dir path
                (max 1000 items).
                if set True, return Iterator of Tuple(remote_path:str,
                file_info:File) for dir and it's children dirs.

        Returns:
            Union[FilesResponse, Iterator[Tuple[str, File]]]:
        """

        if not recursive:
            return cast(
                FilesResponse,
                self.file_api.get_files(
                    project_name,
                    model_name,
                    version_name,
                    dir=dir,
                ),
            )

        return self._list_remote_items(
            project_name=project_name,
            model_name=model_name,
            version=version_name,
            remote_path=dir,
            recursive=True,
            file_only=False,
        )

    @log_call
    def _list_download_items(
        self,
        project_name: str,
        model_name: str,
        version_name: str,
        remote_path: str,
        local_path: str,
    ) -> Iterator[Tuple[str, str, File]]:
        """_list_download_items.

        Args:
            project_name (str): project_name
            model_name (str): model_name
            version_name (str): version_name
            remote_path (str): remote_path
            local_path (str): local_path

        Returns:
            Iterator[Tuple[str, str, StorageFile]]:
        """
        for rpath, file_info in self._list_remote_items(
            project_name,
            model_name,
            version_name,
            remote_path,
            True,
            True,
        ):
            relative_rpath = os.path.relpath(rpath, remote_path)
            lpath = Path(local_path) / relative_rpath
            lpath = os.path.normpath(lpath)
            rpath = (Path("/") / rpath).as_posix()
            yield (rpath, lpath, file_info)

    def _list_local_items(
        self,
        local_path: str,
        remote_path="/",
    ) -> Iterator[Tuple[str, str, File]]:
        for local_file, remote_file in filewalker.walk(local_path, remote_path):
            f = Path(local_file)
            file_info = File(
                isDir=f.is_dir(),
                lastUpdated=f"{f.stat().st_mtime}",
                size=f.stat().st_size,
                name=f.name,
                sha256="",
            )
            yield (local_file, remote_file, file_info)

    def _list_remote_items(
        self,
        project_name: str,
        model_name: str,
        version: str,
        remote_path: str,
        recursive: bool,
        file_only: bool,
        max_page_count: int = 100_000,
    ) -> Iterator[Tuple[str, File]]:
        """_list.

        Args:
            project_name (str): project_name
            model_name (str): model_name
            version (str): version
            remote_path (str): remote_path
            recursive (bool): recursive
            file_only (bool): file_only

        Returns:
            Iterator[Tuple[str, File]]:
        """
        target_paths: List[Path] = [Path(remote_path)]
        while len(target_paths) > 0:
            target_path = target_paths.pop(0)

            # Don't change below "" to None, or marker parameter set by "None".
            continue_marker = ""

            loop_count = 0
            while True:
                resp = cast(
                    FilesResponse,
                    self.file_api.get_files(
                        project_name,
                        model_name,
                        version,
                        dir=target_path.as_posix(),
                        marker=continue_marker,
                    ),
                )

                contents = resp.contents
                if contents:
                    for file_info in contents:
                        remote_path = target_path / file_info.name
                        if file_info.is_dir and recursive:
                            target_paths.append(remote_path)
                            if file_only:
                                continue

                        rpath = remote_path.as_posix()
                        yield (rpath, file_info)

                continue_marker = resp.continue_marker
                if not continue_marker:
                    break

                if loop_count > max_page_count:
                    raise RuntimeError(
                        f"exceeded max loop count({loop_count}>{max_page_count}) on listing model files"  # noqa : E501
                    )
                loop_count += 1


class PublicAPI:
    """PublicAPI."""

    def __init__(self, api_client: ApiClient, debug=False):
        """__init__.

        Args:
            api_client (ApiClient): api_client
            debug (bool): debug flag
        """
        self.debug = debug
        self.api = OriginPublicApi(api_client)

    @log_call
    def list(
        self,
        page: int = 0,
        page_size: int = 30,
        sort_by: str = "",
        ascending: bool = False,
        tags: List[str] = [],
        search="",
    ) -> ModelsResponse:
        """list.

        Args:
            page (int): Page index for pagination (default: 0)
            page_size (int): Page size for pagination (default: 30)
            sort_by (str): Field to sort results on (default: "")
            search (str): Search query string (default: "")
            ascending (bool): Sorts by ascending values if set to true,
                              default is descending  (default: False)
            tags (List[str]): Tags to filter model results on (default: [])

        Returns:
            ModelsResponse:
        """

        return cast(
            ModelsResponse,
            self.api.get_models(
                page=page,
                page_size=page_size,
                sort_by=sort_by,
                ascending=ascending,
                search=search,
                tags=tags,
            ),
        )


class ModelRegistryAPI:
    """Root SDK Class for Model Registry

    Examples:
        Listing models
        ```python
        from mlx.sdk.model_registry import *

        API_ENDPOINT = "<model-regsitry-endpoint>"
        ACCESS_TOKEN = "<access-token>"
        PROJECT_NAME = "<your-project-name>"
        MODEL_NAME = "<your-model-name>"
        VERSION_NAME = "<your-version-name>"

        api = ModelRegistryAPI(API_ENDPOINT, ACCESS_TOKEN)

        # list models
        models = api.model_api.list(PROJECT_NAME)
        print(models)

        # list model files
        files_response = api.file_api.list(
            PROJECT_NAME,
            MODEL_NAME,
            VERSION_NAME,
        )

        for f in files_response.contents:
            print(f)

        # list model files recursive
        result_iterator = api.file_api.list(
            PROJECT_NAME,
            MODEL_NAME,
            VERSION_NAME,
            recursive=True,
        )

        assert isinstance(result_iterator, types.GeneratorType)
        for remote_path, file_info in result_iterator:
            print(remote_path, file_info)
        ```
    """

    def __init__(self, api_endpoint: str, access_token: str = "anonymous", debug=False):
        """__init__.
        Args:
            api_endpoint (str): api_endpoint - can be either base URL
                               (e.g., https://foo.bar.com/xxx) or full
                               model registry endpoint URL
                               (e.g., https://foo.bar.com/xxx/model-registry/api/v1)
            access_token (str): access_token
            debug (bool): debug flag
        """
        conf = Configuration()
        conf.host = self._model_registry_endpoint_url(api_endpoint)
        conf.access_token = access_token
        conf.debug = debug
        conf.proxy = proxy_url(debug)
        self.debug = debug
        self.api_client = ApiClient(conf)
        self.api_client.user_agent = USER_AGENT
        self.access_token = access_token

    def _model_registry_endpoint_url(self, api_endpoint: str) -> str:
        """Build model registry endpoint URL from base or full endpoint.

        Args:
            api_endpoint (str): The input endpoint URL

        Returns:
            str: Model registry endpoint URL with /model-registry/api/v1 path
        """
        # Remove trailing slash if present
        endpoint = api_endpoint.rstrip("/")

        # Check if the endpoint already contains model-registry API path
        if "/model-registry/api/v1" in endpoint:
            return endpoint

        # If not, append the model-registry API path
        return f"{endpoint}/model-registry/api/v1"

    @property
    def health_check_api(self) -> HealthApi:
        """health_check_api property

        Returns:
            HealthApi:
        """
        return HealthApi(self.api_client, self.debug)

    @property
    def model_api(self) -> ModelAPI:
        """model_api property

        Returns:
            ModelAPI:
        """
        return ModelAPI(self.api_client, self.debug)

    @property
    def model_version_api(self) -> ModelVersionAPI:
        """model_version_api property

        Returns:
            ModelVersionAPI:
        """
        return ModelVersionAPI(self.api_client, self.debug)

    @property
    def file_api(self) -> FileAPI:
        """file_api property

        Returns:
            FileAPI:
        """
        return FileAPI(
            self.api_client,
            self.access_token,
            self.debug,
        )

    @property
    def public_api(self) -> PublicAPI:
        """public_api property

        Returns:
            PublicAPI:
        """
        return PublicAPI(self.api_client, self.debug)

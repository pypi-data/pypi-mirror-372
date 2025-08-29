#
# ML expert Platform
# Copyright (c) 2025-present NAVER Cloud Corp.
# Apache-2.0
#

import datetime
from typing import Dict, Iterator, Optional, Tuple

from pydantic import BaseModel, Field


class FileInfo(BaseModel):
    """
    file info record class
    """

    path: str = Field("", description="file path")
    size: int = Field(0, description="file size")
    last_updated: Optional[datetime.datetime] = Field(
        description="file last updated time",
        default=None,
    )


class FileCompList(BaseModel):
    locals: Dict[str, FileInfo] = Field({}, description="list of FileInfo")
    remotes: Dict[str, FileInfo] = Field({}, description="list of FileInfo")

    def add_file_local_info(
        self,
        path: str,
        remote_path: str,
        size: int,
        last_updated: datetime.datetime,
    ):
        self.locals[remote_path] = FileInfo(
            path=path,
            size=size,
            last_updated=last_updated,
        )

    def add_file_remote_info(
        self,
        path: str,
        size: int,
        last_updated: datetime.datetime,
    ):
        self.remotes[path] = FileInfo(
            path=path,
            size=size,
            last_updated=last_updated,
        )

    def is_diff(self) -> bool:
        for _, lf, _, rf in self.each(
            both_exist=True, local_only=False, remote_only=False
        ):
            if lf.size != rf.size:
                return True
            # TODO - handle updated time
        return False

    def exist_local_only(self) -> bool:
        for _, _, _, _ in self.each(
            both_exist=False, local_only=True, remote_only=False
        ):
            return True
        return False

    def exist_remote_only(self) -> bool:
        for _, _, _, _ in self.each(
            both_exist=False, local_only=False, remote_only=True
        ):
            return True
        return False

    def each(
        self,
        both_exist=True,
        local_only=True,
        remote_only=True,
    ) -> Iterator[Tuple[str, FileInfo, str, FileInfo]]:
        for k in self.locals.keys():
            if k in self.remotes.keys():
                if both_exist:
                    yield (
                        self.locals[k].path,
                        self.locals[k],
                        self.remotes[k].path,
                        self.remotes[k],
                    )
            elif local_only:
                yield (
                    self.locals[k].path,
                    self.locals[k],
                    "",
                    None,
                )
        if remote_only:
            for k in self.remotes.keys():
                if k not in self.locals.keys():
                    yield (
                        "",
                        None,
                        self.remotes[k].path,
                        self.remotes[k],
                    )

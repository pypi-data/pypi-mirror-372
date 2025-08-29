#
# ML expert Platform
# Copyright (c) 2025-present NAVER Cloud Corp.
# Apache-2.0
#

import os
from typing import Optional


class Context:
    """Context class for model registry"""

    def __init__(
        self,
        api_endpoint: Optional[str] = None,
        current_project: Optional[str] = None,
        access_token: Optional[str] = None,
    ):
        # first : user parameter first
        self._current_project = current_project
        self._access_token = access_token
        self._api_endpoint = api_endpoint

        # second : env
        self._init_from_env()

        # third : cli command package information
        self._init_from_mlx_cli_command_package()

    def _init_from_env(self):
        if not self._current_project:
            self._current_project = os.getenv("MLX_PROJECT")

        if not self._access_token:
            self._access_token = os.getenv("MLX_APIKEY")

        if not self._api_endpoint:
            # 1st priority: specific model registry endpoint
            self._api_endpoint = os.getenv("MLX_MODEL_REGISTRY_ENDPOINT_URL")

            # 2nd priority: use base MLX endpoint
            if not self._api_endpoint:
                self._api_endpoint = os.getenv("MLX_ENDPOINT_URL")

    def _init_from_mlx_cli_command_package(self):
        try:
            from mlx.sdk.core import config

            cf = config.ConfigFile()
            if not self._current_project:
                self._current_project = cf.project

            if not self._access_token:
                self._access_token = cf.apikey

            if not self._api_endpoint:
                # Use config endpoint_url (normalized by ModelRegistryAPI)
                self._api_endpoint = cf.endpoint_url

        except ModuleNotFoundError:
            return
        except ImportError:
            return

    @property
    def api_endpoint(self) -> Optional[str]:
        return self._api_endpoint

    @property
    def access_token(self) -> Optional[str]:
        return self._access_token

    @property
    def current_project(self) -> Optional[str]:
        return self._current_project

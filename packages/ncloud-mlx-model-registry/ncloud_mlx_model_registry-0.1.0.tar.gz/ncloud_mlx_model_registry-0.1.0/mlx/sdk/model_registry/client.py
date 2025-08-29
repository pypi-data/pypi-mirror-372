#
# ML expert Platform
# Copyright (c) 2025-present NAVER Cloud Corp.
# Apache-2.0
#

from mlx.api.model_registry import (
    ApiClient,
    Configuration,
    FilesApi,
    ModelApi,
    ModelVersionApi,
    PublicApi,
)

from ..user_agent import USER_AGENT
from ..util import proxy_url
from .transport_api import TransportApi
from .transport_client import TransportClient


class ModelRegistry:
    """ModelRegistry."""

    def __init__(self, api_endpoint: str, access_token: str = "anonymous", debug=False):
        """__init__.
        Args:
            api_endpoint (str): api_endpoint
            access_token (str): access_token
            debug:
        """
        conf = Configuration()
        conf.host = api_endpoint
        conf.access_token = access_token
        conf.debug = debug
        conf.proxy = proxy_url(debug)
        self.api_client = ApiClient(conf)
        self.api_client.user_agent = USER_AGENT
        self.transport_client = TransportClient(conf)

    @property
    def model_api(self) -> ModelApi:
        """model_api.
        Returns:
            ModelApi:
        """
        return ModelApi(self.api_client)

    @property
    def model_version_api(self) -> ModelVersionApi:
        """model_version_api.

        Returns:
            ModelVersionApi:
        """
        return ModelVersionApi(self.api_client)

    @property
    def file_api(self) -> FilesApi:
        """file_api.

        Returns:
            FilesApi:
        """
        return FilesApi(self.api_client)

    @property
    def public_api(self) -> PublicApi:
        """public_api.

        Returns:
            PublicApi:
        """
        return PublicApi(self.api_client)

    @property
    def transport_api(self) -> TransportApi:
        """transport_api.

        Returns:
            TransportApi:
        """
        return TransportApi(
            self.transport_client,
        )

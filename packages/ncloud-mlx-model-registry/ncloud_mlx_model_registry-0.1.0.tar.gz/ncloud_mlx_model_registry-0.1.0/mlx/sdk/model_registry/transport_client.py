#
# ML expert Platform
# Copyright (c) 2025-present NAVER Cloud Corp.
# Apache-2.0
#

from typing import AsyncIterable, BinaryIO
from urllib.parse import urlparse

import httpx

from mlx.api.model_registry import Configuration

from .util import proxy_url


class TransportClient:
    def __init__(self, configuration: Configuration, retries=3):
        self.conf = configuration
        self.retries = retries

    async def open(self):
        headers = {}
        self.update_params_for_auth(headers, ["OAuth2Application", "bearerAuth"])
        timeout = httpx.Timeout(
            timeout=60.0  # default 60s (read, write, pool, connect)
        )
        transport = httpx.AsyncHTTPTransport(
            retries=self.retries, verify=self.conf.verify_ssl
        )
        self.client = httpx.AsyncClient(
            headers=headers,
            timeout=timeout,
            transport=transport,
            # See : https://www.python-httpx.org/advanced/#http-proxying
            proxies=proxy_url(self.conf.debug),
            verify=self.conf.verify_ssl,
        )

    async def close(self):
        if self.client:
            await self.client.aclose()

    async def post(
        self,
        resource_path: str,
        data: AsyncIterable,
        headers: dict = None,
        params: dict = None,
        force_http: bool = False,
    ):
        host_url = self.conf.host
        if force_http:
            host_url = self.replace_scheme(self.conf.host, "http")

        url = host_url + resource_path
        response = await self.client.post(
            url,
            content=data,
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        return response

    async def put(
        self,
        resource_path: str,
        data: AsyncIterable,
        headers: dict = None,
        params: dict = None,
        force_http: bool = False,
    ):
        host_url = self.conf.host
        if force_http:
            host_url = self.replace_scheme(self.conf.host, "http")

        url = host_url + resource_path
        response = await self.client.put(
            url,
            content=data,
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        return response

    async def get(
        self,
        resource_path: str,
        data: BinaryIO,
        headers: dict = None,
        params: dict = None,
        force_http: bool = False,
    ):
        host_url = self.conf.host
        if force_http:
            host_url = self.replace_scheme(self.conf.host, "http")

        url = host_url + resource_path

        async with self.client.stream(
            "GET", url, headers=headers, params=params
        ) as response:
            response.raise_for_status()
            async for chunk in response.aiter_bytes():
                data.write(chunk)

    def update_params_for_auth(self, headers, auth_settings):
        if not auth_settings:
            return

        for auth in auth_settings:
            auth_setting = self.conf.auth_settings().get(auth)
            if auth_setting:
                if not auth_setting["value"]:
                    continue
                elif auth_setting["in"] == "header":
                    headers[auth_setting["key"]] = auth_setting["value"]
                else:
                    raise ValueError(
                        "Authentication token must be in `query` or `header`"
                    )

    def replace_scheme(self, url: str, scheme: str) -> str:
        o = urlparse(url)
        o = o._replace(scheme=scheme)
        return o.geturl()

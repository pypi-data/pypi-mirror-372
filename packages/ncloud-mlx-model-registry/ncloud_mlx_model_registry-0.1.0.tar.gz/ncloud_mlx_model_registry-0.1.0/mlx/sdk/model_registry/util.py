#
# ML expert Platform
# Copyright (c) 2025-present NAVER Cloud Corp.
# Apache-2.0
#

import logging
import os
from urllib.request import getproxies

LOGGER_NAME = "mlx.sdk.model_registry"

NAMESPACE_PREFIX = "mlx-n-"

logger = logging.getLogger(LOGGER_NAME)


def project_name_to_namespace(project_name: str) -> str:
    if not project_name:
        return ""
    return f"{NAMESPACE_PREFIX}{project_name}"


def namespace_to_project_name(namespace: str) -> str:
    if not namespace.startswith(NAMESPACE_PREFIX):
        return ""
    return namespace.removeprefix(NAMESPACE_PREFIX)


def config_dir(app_name: str) -> str:
    if not app_name:
        raise RuntimeError("app_name required")

    path = f"~/.config/{app_name}"
    path = os.path.abspath(os.path.expanduser(path))
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def config_path(app_name: str, file_name="config.yaml") -> str:
    return os.path.join(config_dir(app_name), file_name)


def proxy_url(debug=False):
    proxies = getproxies()
    try:
        url = proxies["https"]
        if debug:
            print(f"Uses proxy env variable https_proxy == '{url}'")
        return url
    except KeyError:
        pass

    return None


def model_uri(endpoint: str, project: str, model: str, version: str) -> str:
    # remove possible schema and trailing slash from registry endpoint
    endpoint = endpoint.split("://")[-1].strip("/")
    return f"mlx+model-registry://{endpoint}/projects/{project}/models/{model}/versions/{version}"


def log_call(func):
    def wrapper(*args, **kwargs):
        logger.debug(f"-> {func.__name__} {args} {kwargs}")
        result = func(*args, **kwargs)
        logger.debug(f"<- {func.__name__} returned {result}")
        return result

    return wrapper

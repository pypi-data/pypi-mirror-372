#
# ML expert Platform
# Copyright (c) 2025-present NAVER Cloud Corp.
# Apache-2.0
#

from typing import Type

import requests

from mlx.sdk.core.config import ConfigFile

__all__ = ["api_client", "BaseMLXWebappAPI"]


def api_client(
    mlx_webapp_endpoint: str,
    api_key: str = None,
    api_cls: Type["BaseMLXWebappAPI"] = None,
    debug: bool = False,
    **kwargs,
):
    """
    Create an API client instance.

    :param mlx_webapp_endpoint: MLX api server endpoint
            :param api_key: API key for authentication (optional).
                        If not provided, will be loaded from:
                        1. Environment variable: MLX_APIKEY
                        2. Config file (set via 'mlx configure' command)
    :param api_cls: API class to instantiate
    :param debug: Enable debug mode
    :param kwargs: Additional arguments to pass to the API class
    :return: API client instance

    Example:
        # Method 1: Pass API key directly
        client = api_client(
            "https://api.example.com",
            api_key="your-api-key",
            api_cls=SomeAPI
        )

        # Method 2: Use environment variable
        # export MLX_APIKEY="your-api-key"
        client = api_client("https://api.example.com", api_cls=SomeAPI)

        # Method 3: Use config file (set via CLI)
        # mlx configure
        client = api_client("https://api.example.com", api_cls=SomeAPI)
    """
    if not api_key:
        config_file = ConfigFile()
        api_key = config_file.apikey

    if not api_key:
        raise ValueError(
            "API key is required. You can set it by:\n"
            "  1. Environment variable: export MLX_APIKEY='your-api-key'\n"
            "  2. CLI command: mlx configure\n"
            "  3. Pass as api_key argument to the function"
        )

    kwargs.update(
        {
            "mlx_webapp_endpoint": mlx_webapp_endpoint,
            "api_key": api_key,
            "debug": debug,
        }
    )

    return api_cls(**kwargs)


class BaseMLXWebappAPI:
    """
    Api class to provide basic methods.
    """

    def __init__(
        self,
        mlx_webapp_endpoint: str,
        api_key: str,
        debug: bool = False,
    ):
        """
        BaseApi constructor.

        :param mlx_webapp_endpoint: MLX api server endpoint(Webapp)
        :param api_key: API key for authentication
        :param debug: Provide detailed trace to debug
        """

        self._debug = debug
        self._mlx_webapp_endpoint = mlx_webapp_endpoint
        self.api_key = api_key

    @property
    def api_headers(self):
        return {"Authorization": f"Bearer {self.api_key}"}

    def api_get(self, path: str, as_dict: bool = True, **kwargs):
        """
        GET Api wrapper.
        TODO : replace to swagger API

        :param path: api path
        :param as_dict: return as dict type
        :param kwargs: query params
        :return: response
        """
        data = kwargs if kwargs else {}
        response = requests.get(
            f"{self._mlx_webapp_endpoint}{path}", headers=self.api_headers, data=data
        )
        if response.status_code != 200:
            raise RuntimeError(
                f"Failed to get {path} with status code {response.status_code}"
            )
        if as_dict:
            try:
                return response.json()
            except ValueError:
                raise RuntimeError(f"Failed to parse response as JSON: {response.text}")
        return response.text

    def api_post(self, path: str, as_dict: bool = True, **kwargs):
        """
        POST Api wrapper.
        TODO : replace to swagger API

        :param path: api path
        :param as_dict: return as dict type
        :param kwargs: query params
        :return: response
        """
        data = kwargs if kwargs else {}
        response = requests.post(
            f"{self._mlx_webapp_endpoint}{path}", headers=self.api_headers, json=data
        )
        if response.status_code != 200:
            raise RuntimeError(
                f"Failed to get {path} with status code {response.status_code}"
            )
        if as_dict:
            try:
                return response.json()
            except ValueError:
                raise RuntimeError(f"Failed to parse response as JSON: {response.text}")
        return response.text

    def api_delete(self, path: str, as_dict: bool = True, **kwargs):
        """
        DELETE Api wrapper.
        TODO : replace to swagger API

        :param path: api path
        :param as_dict: return as dict type
        :param kwargs: query params
        :return: response
        """
        data = kwargs if kwargs else {}
        response = requests.delete(
            f"{self._mlx_webapp_endpoint}{path}", headers=self.api_headers, data=data
        )
        if response.status_code != 200:
            raise RuntimeError(
                f"Failed to get {path} with status code {response.status_code}"
            )
        if as_dict:
            try:
                return response.json()
            except ValueError:
                raise RuntimeError(f"Failed to parse response as JSON: {response.text}")
        return response.text

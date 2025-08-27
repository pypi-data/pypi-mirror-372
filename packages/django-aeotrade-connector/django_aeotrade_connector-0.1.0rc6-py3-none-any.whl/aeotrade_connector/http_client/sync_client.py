"""
@company: 慧贸天下(北京)科技有限公司
@author: wanghao@aeotrade.com
@time: 2024/12/9 11:08
@file: sync_client.py
@project: django_aeotrade_connector
@describe: None
"""
from typing import Any, Dict, Optional, Tuple, Type, Union

import httpx

from aeotrade_connector.schemas import RWModel
from aeotrade_connector.utils import validate_url

T_SyncHTTPClientResponse = Tuple[bool, Union[httpx.Response, str]]
T_RWModelData = Union[Type[RWModel], Dict[str, Any], None]


class SyncHttpClient:
    """
    Synchronous HTTP Client based on httpx.
    """

    DEFAULT_TIMEOUT: int = 15  # Default timeout in seconds

    def __init__(self):
        self.client = httpx.Client()

    def __enter__(self):
        # Initialize resources when entering the context
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Close the httpx client when exiting the context
        self.client.close()

    def _request(
            self,
            url: str,
            method: str = "GET",
            headers: Optional[Dict[str, str]] = None,
            data: Optional[Union[Dict[str, Any], str]] = None,
            json: Optional[Dict[str, Any]] = None,
            timeout: int = DEFAULT_TIMEOUT,
            **kwargs,
    ) -> T_SyncHTTPClientResponse:
        _ok = False
        try:
            response = self.client.request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                json=json,
                timeout=timeout,
                **kwargs,
            )
            response.raise_for_status()
            _ok = True
            return _ok, response
        except httpx.RequestError as e:
            err_msg = f"[SyncHttpClient] Request error: {e}"
        except httpx.HTTPStatusError as e:
            err_msg = f"[SyncHttpClient] HTTP status error: {e.response.status_code} {e.response.text}"
        except Exception as e:
            err_msg = f"[SyncHttpClient] An unexpected error occurred: {e}"
        return _ok, err_msg

    @staticmethod
    def _model_to_dict(data: T_RWModelData) -> Optional[dict]:
        if issubclass(type(data), RWModel):
            return data.to_dict()  # type: ignore[union-attr, call-arg]
        return data  # type: ignore[return-value]

    @staticmethod
    def url_validator(url, host, path):
        if host and path:
            url = f'{host}{path}'

        if not url:
            raise ValueError("[Aeotrade Connector]-[AsyncHttpClient] URL is required")

        if not validate_url(url):
            raise ValueError(f"[Aeotrade Connector]-[AsyncHttpClient] Invalid URL: {url}")
        return url

    def get(
            self,
            url: Optional[str] = None,
            *,
            host: Optional[str] = None,
            path: Optional[str] = None,
            headers: T_RWModelData = None,
            timeout: int = DEFAULT_TIMEOUT,
            **kwargs,
    ) -> T_SyncHTTPClientResponse:
        """
        Send a GET request to the given URL.
        """
        url = self.url_validator(url, host, path)
        return self._request(
            url,  # type: ignore[arg-type]
            method="GET",
            headers=self._model_to_dict(headers),
            timeout=timeout, **kwargs
        )

    def post(
            self,
            url: Optional[str] = None,
            *,
            host: Optional[str] = None,
            path: Optional[str] = None,
            data: T_RWModelData = None,
            json: T_RWModelData = None,
            headers: T_RWModelData = None,
            timeout: int = DEFAULT_TIMEOUT,
            **kwargs,
    ) -> T_SyncHTTPClientResponse:
        """
        Send a POST request to the given URL.
        """
        url = self.url_validator(url, host, path)
        return self._request(
            url,  # type: ignore[arg-type]
            method='POST',
            headers=self._model_to_dict(headers),
            data=self._model_to_dict(data),
            json=self._model_to_dict(json),
            timeout=timeout,
            **kwargs
        )

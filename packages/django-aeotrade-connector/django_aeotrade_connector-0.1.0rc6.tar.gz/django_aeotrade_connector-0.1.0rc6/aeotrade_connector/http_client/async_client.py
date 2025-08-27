"""
@company: 慧贸天下(北京)科技有限公司
@author: wanghao@aeotrade.com
@time: 2024/12/9 11:08
@file: async_client.py
@project: django_aeotrade_connector
@describe: None
"""
import asyncio
import logging
from typing import Any, ClassVar, Dict, Optional, Tuple, Type, Union

try:
    import aiohttp
    from aiohttp.typedefs import DEFAULT_JSON_DECODER
except ImportError as exc:  # pragma: nocover
    raise ImportError("AsyncHttpClient requires aiohttp installed") from exc

from aeotrade_connector.schemas import RWModel
from aeotrade_connector.utils import validate_url

logger = logging.getLogger('log')


class AsyncHttpClientResponse:

    def __init__(self, response: aiohttp.ClientResponse):
        self.status = response.status
        self.headers = response.headers
        self._response = response  # source response
        self._raw_text = None  # original text
        self._text = None
        self._json = None

    async def auto_read(self):
        self._raw_text = await self._response.text()
        self._text = self._raw_text
        try:
            self._text = await self._response.text()
            self._json = await self._response.json()
        except aiohttp.ContentTypeError:
            self._json = None

    def text(self, encoding: Optional[str] = None, errors: str = "strict") -> str:
        """
        Read response payload and decode.

        Args:
            encoding: (optional) Response encoding.
            errors: (optional) How to handle invalid characters.

        Returns:
            Decoded text.
        """

        if encoding is None:
            encoding = self._text

        if self._raw_text is None:
            return ""

        return self._raw_text.encode(self._response.get_encoding()).decode(encoding, errors)

    def json(self, encoding: Optional[str] = None, loads=DEFAULT_JSON_DECODER,
             content_type: Optional[str] = "application/json") -> Any:
        """
        Read response payload and decode with JSON decoder.

        Args:
            encoding: (optional) Response encoding.
            loads: (optional) Callable to deserialize JSON data.
            content_type: (optional) Expected response content type.

        Returns:
            Deserialized JSON data.
        """

        if content_type and content_type not in self.headers.get("Content-Type", ""):
            raise ValueError(f"[Aeotrade Connector] Unexpected content type: {self.headers.get('Content-Type')}")

        if self._json is not None:
            return self._json

        if self._raw_text is None:
            return {}

        if encoding is not None:
            raw_text = self._raw_text.encode(self._response.get_encoding()).decode(encoding)
        else:
            raw_text = self._text

        return loads(raw_text)


T_AsyncHTTPClientResponse = Tuple[bool, Union[AsyncHttpClientResponse, str]]
T_RWModelData = Union[Type[RWModel], Dict[str, Any], None]


class AsyncHttpClient:
    """
    Async HTTP Client, Based on aiohttp
    """

    DEFAULT_TIMEOUT: ClassVar[int] = 15  # 15 seconds

    def __init__(self):
        self.session = aiohttp.ClientSession()

    async def _request(
            self,
            url,
            method='GET',
            headers=None,
            data=None,
            json=None,
            timeout=10,
            **kwargs
    ) -> T_AsyncHTTPClientResponse:
        _ok = False
        try:
            async with self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=data,
                    json=json,
                    timeout=timeout,
                    **kwargs
            ) as response:
                response.raise_for_status()
                client_response = AsyncHttpClientResponse(response)
                await client_response.auto_read()
                _ok = True
                return _ok, client_response
        except aiohttp.ClientConnectorError as e:
            err_msg = f"[AsyncHttpClient] [ClientConnectorError]: {e}"
        except aiohttp.ClientError as e:
            err_msg = f"[AsyncHttpClient] Client error: {e}"
        except asyncio.TimeoutError:
            err_msg = "[AsyncHttpClient] Request timed out"
        except Exception as e:
            err_msg = f"[AsyncHttpClient] An error occurred: {e}"
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

    async def get(
            self,
            url: Optional[str] = None,
            *,
            host: Optional[str] = None,
            path: Optional[str] = None,
            headers: T_RWModelData = None,
            timeout: int = DEFAULT_TIMEOUT,
            **kwargs
    ) -> T_AsyncHTTPClientResponse:
        url = self.url_validator(url, host, path)
        return await self._request(url, method='GET', headers=self._model_to_dict(headers), timeout=timeout, **kwargs)

    async def post(
            self,
            url: Optional[str] = None,
            *,
            host: Optional[str] = None,
            path: Optional[str] = None,
            data: T_RWModelData = None,
            json: T_RWModelData = None,
            headers: T_RWModelData = None,
            timeout: int = DEFAULT_TIMEOUT,
            **kwargs
    ) -> T_AsyncHTTPClientResponse:
        """
        Send POST request to given URL.
        :param url:  HTTP URL to send request to.
        :param host: URL host
        :param path: URL path
        :param data: data
        :param json: json data
        :param headers: request headers
        :param timeout: timeout, default 15
        :param kwargs: other kwargs
        :return: T_AsyncHTTPClientResponse
        Tips:
            - `host` and `path` are optional, if `host` and `path` is given, url will be ignored
        """
        url = self.url_validator(url, host, path)

        return await self._request(
            url,
            method='POST',
            headers=self._model_to_dict(headers),
            data=self._model_to_dict(data),
            json=self._model_to_dict(json),
            timeout=timeout,
            **kwargs
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

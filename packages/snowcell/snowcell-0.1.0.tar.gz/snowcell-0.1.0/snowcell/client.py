import asyncio
import os
import random
import time
from typing import Any, Type, Union

import httpx
from snowcell.__about__ import __version__
from snowcell.exceptions import SnowcellError
from snowcell.chat import Chat
from snowcell.completion import Completions


# Defaults (override with env vars or constructor args)
DEFAULT_API_BASE_URL = os.environ.get("SNOWCELL_API_BASE_URL", "https://api.snowcell.io")
DEFAULT_INFERENCE_BASE_URL = os.environ.get("SNOWCELL_INFERENCE_BASE_URL", "https://inference.snowcell.io")
DEFAULT_TIMEOUT = httpx.Timeout(5.0, read=300.0, write=30.0, connect=5.0)


class Snowcell:
    """Snowcell SDK client."""

    __api_client: httpx.Client | None = None
    __inf_client: httpx.Client | None = None
    __api_async_client: httpx.AsyncClient | None = None
    __inf_async_client: httpx.AsyncClient | None = None

    def __init__(
        self,
        api_token: str | None = None,
        *,
        api_base_url: str | None = None,
        inference_base_url: str | None = None,
        timeout: httpx.Timeout | float | None = None,
        **kwargs: Any,
    ) -> None:
        self._api_token = api_token or os.environ.get("SNOWCELL_API_TOKEN")
        self._api_base_url = (api_base_url or DEFAULT_API_BASE_URL).rstrip("/")
        self._inference_base_url = (inference_base_url or DEFAULT_INFERENCE_BASE_URL).rstrip("/")
        self._timeout = timeout or DEFAULT_TIMEOUT
        self._client_kwargs = kwargs

    # ---- httpx client builders -------------------------------------------------

    def _build_httpx_client(
        self,
        client_type: Type[Union[httpx.Client, httpx.AsyncClient]],
        base_url: str,
    ) -> Union[httpx.Client, httpx.AsyncClient]:
        headers = {
            "User-Agent": f"snowcell-python/{__version__}",
            "Authorization": f"Bearer {self._api_token}",
            "Content-Type": "application/json",
        }
        if client_type is httpx.Client:
            transport = RetryTransport(httpx.HTTPTransport())
            return httpx.Client(base_url=base_url, headers=headers, timeout=self._timeout, transport=transport)
        else:
            transport = RetryTransport(httpx.AsyncHTTPTransport())
            return httpx.AsyncClient(base_url=base_url, headers=headers, timeout=self._timeout, transport=transport)

    def _api_client(self) -> httpx.Client:
        if not self.__api_client:
            self.__api_client = self._build_httpx_client(httpx.Client, self._api_base_url)
        return self.__api_client

    def _inference_client(self) -> httpx.Client:
        if not self.__inf_client:
            self.__inf_client = self._build_httpx_client(httpx.Client, self._inference_base_url)
        return self.__inf_client

    def _api_async_client(self) -> httpx.AsyncClient:
        if not self.__api_async_client:
            self.__api_async_client = self._build_httpx_client(httpx.AsyncClient, self._api_base_url)
        return self.__api_async_client

    def _inference_async_client(self) -> httpx.AsyncClient:
        if not self.__inf_async_client:
            self.__inf_async_client = self._build_httpx_client(httpx.AsyncClient, self._inference_base_url)
        return self.__inf_async_client

    # ---- request helpers (resources call these) --------------------------------

    def _api_request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        resp = self._api_client().request(method, path, **kwargs)
        self._raise_for_status(resp)
        return resp

    async def _api_async_request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        resp = await self._api_async_client().request(method, path, **kwargs)
        self._raise_for_status(resp)
        return resp

    def _inference_request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        resp = self._inference_client().request(method, path, **kwargs)
        self._raise_for_status(resp)
        return resp

    async def _inference_async_request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        resp = await self._inference_async_client().request(method, path, **kwargs)
        self._raise_for_status(resp)
        return resp

    def _inference_stream(self, method: str, path: str, **kwargs: Any):
        return self._inference_client().stream(method, path, **kwargs)

    async def _inference_async_stream(self, method: str, path: str, **kwargs: Any):
        return self._inference_async_client().stream(method, path, **kwargs)

    # ---- error mapping ---------------------------------------------------------

    def _raise_for_status(self, resp: httpx.Response) -> None:
        if 400 <= resp.status_code < 600:
            raise SnowcellError.from_response(resp)

    # ---- GA resources (inference) ---------------------------------------------

    @property
    def chat(self) -> Chat:
        return Chat(client=self)

    @property
    def completions(self) -> Completions:
        return Completions(client=self)


class RetryTransport(httpx.AsyncBaseTransport, httpx.BaseTransport):
    """
    Simple retry wrapper:
      - Retries ONLY idempotent methods (HEAD, GET, PUT, DELETE, OPTIONS, TRACE)
      - Retries on {429, 503, 504}
      - Honors numeric Retry-After when present
      - Exponential backoff with jitter
    """
    RETRYABLE_METHODS = {"HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"}
    RETRYABLE_STATUS_CODES = {429, 503, 504}
    MAX_BACKOFF_WAIT = 60

    def __init__(
        self,
        wrapped_transport: httpx.BaseTransport | httpx.AsyncBaseTransport,
        *,
        max_attempts: int = 10,
        backoff_factor: float = 0.1,
        jitter_ratio: float = 0.1,
    ) -> None:
        self._wrapped_transport = wrapped_transport
        self.max_attempts = max_attempts
        self.backoff_factor = backoff_factor
        self.jitter_ratio = jitter_ratio

    def _calculate_sleep(self, attempts_made: int) -> float:
        backoff = self.backoff_factor * (2 ** (attempts_made - 1))
        jitter = backoff * self.jitter_ratio * random.choice([1, -1])
        return min(backoff + jitter, self.MAX_BACKOFF_WAIT)

    # ---- Sync -----------------------------------------------------------------
    def handle_request(self, request: httpx.Request) -> httpx.Response:
        method = request.method.upper()
        if method not in self.RETRYABLE_METHODS:
            return self._wrapped_transport.handle_request(request)

        last_response: httpx.Response | None = None
        for attempt in range(1, self.max_attempts + 1):
            response = self._wrapped_transport.handle_request(request)
            if response.status_code not in self.RETRYABLE_STATUS_CODES:
                return response
            last_response = response
            response.close()
            retry_after = response.headers.get("retry-after")
            sleep_s = float(retry_after) if retry_after and retry_after.isdigit() else self._calculate_sleep(attempt)
            time.sleep(sleep_s)
        # Give back the last error if all retries exhausted
        assert last_response is not None
        return last_response

    # ---- Async ----------------------------------------------------------------
    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        method = request.method.upper()
        if method not in self.RETRYABLE_METHODS:
            return await self._wrapped_transport.handle_async_request(request)

        last_response: httpx.Response | None = None
        for attempt in range(1, self.max_attempts + 1):
            response = await self._wrapped_transport.handle_async_request(request)
            if response.status_code not in self.RETRYABLE_STATUS_CODES:
                return response
            last_response = response
            await response.aclose()
            retry_after = response.headers.get("retry-after")
            sleep_s = float(retry_after) if retry_after and retry_after.isdigit() else self._calculate_sleep(attempt)
            await asyncio.sleep(sleep_s)
        assert last_response is not None
        return last_response

from __future__ import annotations

import json
from typing import Any, Iterator, AsyncIterator, TYPE_CHECKING

from snowcell.schemas import ChatCompletionResponse

if TYPE_CHECKING:
    from snowcell.client import Snowcell


class Chat:
    def __init__(self, client: Snowcell):
        self._client = client

    def create(
        self,
        model: str,
        messages: list[dict],
        max_tokens: int = 512,
        temperature: float = 0.7,
        stream: bool = False,
        **kwargs: Any,
    ) -> ChatCompletionResponse:
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream,
            **kwargs,
        }
        resp = self._client._inference_request("POST", "/v1/chat/completions", json=payload)
        return ChatCompletionResponse(**resp.json())

    async def acreate(
        self,
        model: str,
        messages: list[dict],
        max_tokens: int = 512,
        temperature: float = 0.7,
        stream: bool = False,
        **kwargs: Any,
    ) -> ChatCompletionResponse:
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream,
            **kwargs,
        }
        resp = await self._client._inference_async_request("POST", "/v1/chat/completions", json=payload)
        return ChatCompletionResponse(**resp.json())

    def stream(
        self,
        model: str,
        messages: list[dict],
        max_tokens: int = 512,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> Iterator[dict]:
        """
        Synchronous generator yielding each SSE chunk as a dict.
        """
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
            **kwargs,
        }
        with self._client._inference_client().stream(
            "POST", "/v1/chat/completions", json=payload, headers={"Accept": "text/event-stream"}
        ) as response:
            for line in response.iter_lines():
                if not line:
                    continue
                if line.startswith("data:"):
                    data = line.removeprefix("data:").strip()
                    if data == "[DONE]":
                        break
                    yield json.loads(data)

    async def astream(
        self,
        model: str,
        messages: list[dict],
        max_tokens: int = 512,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> AsyncIterator[dict]:
        """
        Async generator yielding each SSE chunk as a dict.
        """
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
            **kwargs,
        }
        async with self._client._inference_async_client().stream(
            "POST", "/v1/chat/completions", json=payload, headers={"Accept": "text/event-stream"}
        ) as response:
            async for line in response.aiter_lines():
                if not line:
                    continue
                if line.startswith("data:"):
                    data = line.removeprefix("data:").strip()
                    if data == "[DONE]":
                        break
                    yield json.loads(data)

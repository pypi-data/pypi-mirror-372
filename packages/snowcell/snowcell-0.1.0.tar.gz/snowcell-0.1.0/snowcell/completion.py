from __future__ import annotations

from typing import Any, TYPE_CHECKING

from snowcell.schemas import CompletionResponse

if TYPE_CHECKING:
    from snowcell.client import Snowcell


class Completions:
    def __init__(self, client: "Snowcell"):
        self._client = client

    def create(
        self,
        model: str,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        stream: bool = False,
        **kwargs: Any,
    ) -> CompletionResponse:
        payload = {
            "model": model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream,
            **kwargs,
        }
        # Use the inference origin
        resp = self._client._inference_request("POST", "/v1/completions", json=payload)
        return CompletionResponse(**resp.json())

    async def acreate(
        self,
        model: str,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        stream: bool = False,
        **kwargs: Any,
    ) -> CompletionResponse:
        payload = {
            "model": model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream,
            **kwargs,
        }
        resp = await self._client._inference_async_request("POST", "/v1/completions", json=payload)
        return CompletionResponse(**resp.json())

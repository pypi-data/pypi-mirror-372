from abc import ABC
from typing import Any, Generic, Sequence, TypeVar

import httpx

from ..types import AsyncMarker, Message

ClientT = TypeVar("ClientT")


class _Llm(Generic[ClientT]):
    api_key: str
    base_url: str
    client: ClientT

    def completion(self, *args, **kwargs) -> Any: ...


class SyncLlm(ABC, _Llm[httpx.Client]):
    def completion(self, *, messages: Sequence[Message]) -> str: ...


class AsyncLlm(ABC, _Llm[httpx.AsyncClient], AsyncMarker):
    async def completion(self, *, messages: Sequence[Message]) -> str: ...

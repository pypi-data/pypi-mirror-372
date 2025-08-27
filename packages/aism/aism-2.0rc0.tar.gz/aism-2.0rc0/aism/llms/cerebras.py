from typing import Literal, Optional, Sequence
import httpx

from ._abc import AsyncLlm, SyncLlm
from ._utils import safe_base_url, try_getenv
from ..types import Message

CEREBRAS_API_BASE = "https://api.cerebras.ai/v1"
CEREBRAS_DEFAULT_MODEL = "gpt-oss-120b"

ReasoningEffort = Literal["low", "medium", "high"]


class AsyncCerebras(AsyncLlm):
    model: str
    reasoning_effort: Optional[ReasoningEffort]

    def __init__(
        self,
        model: str = CEREBRAS_DEFAULT_MODEL,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        reasoning_effort: Optional[ReasoningEffort] = None,
    ):
        self.api_key = api_key or try_getenv("CEREBRAS_API_KEY")
        self.base_url = safe_base_url(base_url or CEREBRAS_API_BASE)
        self.client = httpx.AsyncClient(
            headers={"Authorization": "Bearer " + self.api_key}
        )
        self.model = model
        self.reasoning_effort = reasoning_effort

    async def completion(self, *, messages: Sequence[Message]) -> str:
        res = await self.client.post(
            self.base_url + "/chat/completions",
            json={
                "model": self.model,
                "messages": messages,
                "stream": False,
                "max_completion_tokens": 65536,
                "reasoning_effort": self.reasoning_effort,
            },
        )
        content = res.json()["choices"][0]["message"]["content"]
        assert content, "No content"

        return content


class Cerebras(SyncLlm):
    """A model from Cerebras.

    Args:
        model (str): The model. Defaults to `gpt-oss-120b`.
        api_key (str, optional): API key. Uses environ variable: `CEREBRAS_API_KEY`.
        base_url (str, optional): API base URL.
        reasoning_effort (str, optional): Reasoning effort, if the model supports it.
    """

    model: str
    reasoning_effort: Optional[ReasoningEffort]

    def __init__(
        self,
        model: str = CEREBRAS_DEFAULT_MODEL,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        reasoning_effort: Optional[ReasoningEffort] = None,
    ):
        self.api_key = api_key or try_getenv("CEREBRAS_API_KEY")
        self.base_url = safe_base_url(base_url or CEREBRAS_API_BASE)
        self.client = httpx.Client(headers={"Authorization": "Bearer " + self.api_key})
        self.model = model
        self.reasoning_effort = reasoning_effort

    def completion(self, *, messages: Sequence[Message]) -> str:
        res = self.client.post(
            self.base_url + "/chat/completions",
            json={
                "model": self.model,
                "messages": messages,
                "stream": False,
                "max_completion_tokens": 65536,
                "reasoning_effort": self.reasoning_effort,
            },
        )
        content = res.json()["choices"][0]["message"]["content"]
        assert content, "No content"

        return content

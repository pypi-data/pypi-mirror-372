from typing_extensions import Sequence

from ._abc import AsyncLlm, SyncLlm
from ..types import Message


class AsyncChainedLlm(AsyncLlm):
    def __init__(self, llms: Sequence[AsyncLlm]):
        self.llms = llms

    async def completion(self, *, messages: Sequence[Message]) -> str:
        tracebacks = []

        for llm in self.llms:
            try:
                res = await llm.completion(messages=messages)
                return res
            except Exception as err:
                tracebacks.append(llm.__name__ + ": " + str(err))
        else:
            raise RuntimeError(
                "failed to run completions with any llm given:\n- "
                + "\n- ".join(tracebacks)
            )


class ChainedLlm(SyncLlm):
    def __init__(self, llms: Sequence[SyncLlm]):
        self.llms = llms

    def completion(self, *, messages: Sequence[Message]) -> str:
        tracebacks = []

        for llm in self.llms:
            try:
                res = llm.completion(messages=messages)
                return res
            except Exception as err:
                tracebacks.append(llm.__name__ + ": " + str(err))
        else:
            raise RuntimeError(
                "failed to run completions with any llm given:\n- "
                + "\n- ".join(tracebacks)
            )

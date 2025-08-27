"""Wrappers.

If you're finding the source of Aism, go to `_aism.py` and find the class `Aism`.
"""

from typing import Literal, Optional, TypeVar, Union

from ._aism import _Aism, GiveSession

from .data import StructuredItem
from .models import Reasoned
from .types import PydanticModelLike, StructuredDataclassInstance

FillableT = TypeVar(
    "FillableT", bound=Union[type[StructuredDataclassInstance], type[PydanticModelLike]]
)

class SyncSession(GiveSession):
    def give(
        self, *items: StructuredItem, label: Optional[str] = None
    ) -> "SyncSession": ...
    def fill(self, dc: FillableT) -> Reasoned[FillableT]: ...
    def prompt(self, s: str, /) -> str: ...
    def describe(self, mode: Literal["concise", "summary"] = "summary") -> str: ...
    def mentioned(self, snippet: str, /) -> Reasoned[Union[bool, Literal["partial"]]]:
        """Checks if the term/concept is mentioned in the data.

        Returns `"partial"` if only partial of the term is mentioned.

        Note that if it **can be inferred** from the given context (even if
        not directly said), `True` is still returned.

        Args:
            snippet (str): The snippet.

        Returns:
            Reasoned[Union[bool, Literal["partial"]]]: True/False/"partial".
        """

    def compare(self, *, topic: Optional[str] = None) -> str: ...

class AsyncSession(GiveSession):
    def give(
        self, *items: StructuredItem, label: Optional[str] = None
    ) -> "AsyncSession": ...
    async def fill(self, dc: FillableT, /) -> Reasoned[FillableT]: ...
    async def prompt(self, s: str, /) -> str: ...
    async def describe(
        self, mode: Literal["concise", "summary"] = "summary"
    ) -> str: ...
    async def mentioned(
        self, snippet: str, /
    ) -> Reasoned[Union[bool, Literal["partial"]]]:
        """Checks if the term/concept is mentioned in the data. (Async)

        Returns `"partial"` if only partial of the term is mentioned.

        Note that if it **can be inferred** from the given context (even if
        not directly said), `True` is still returned.

        Args:
            snippet (str): The snippet.

        Returns:
            Reasoned[Union[bool, Literal["partial"]]]: True/False/"partial".
        """

    async def compare(self, *, topic: Optional[str] = None) -> str: ...

class Aism(_Aism):
    """⛰️ AI for the runtime.

    Args:
        llm: The LLM(s) to use. Could be a list of LLMs to use or just one.

    Example:
    ```python
    from aism.llms import Cerebras

    # one model
    ai = Aism(Cerebras())


    # ...or more
    ai = Aism([
        Cerebras("model-1"),
        Cerebras("model-2"),
        ...
    ])
    ```
    """

    def give(
        self, *items: StructuredItem, label: Optional[str] = None
    ) -> "SyncSession": ...

class AsyncAism(_Aism):
    """⛰️ AI for the runtime. Async.

    Args:
        llm: The LLM(s) to use. Could be a list of LLMs to use or just one.

    Example:
    ```python
    from aism.llms import AsyncCerebras

    # one model
    ai = AsyncAism(AsyncCerebras())


    # ...or more
    ai = AsyncAism([
        AsyncCerebras("model-1"),
        AsyncCerebras("model-2"),
        ...
    ])
    ```
    """

    def give(
        self, *items: StructuredItem, label: Optional[str] = None
    ) -> "AsyncSession": ...

from typing import Any, Literal, Optional, Union
from typing_extensions import MutableSequence, Self, Sequence

import rjsonc

from .llms._abc import AsyncLlm, SyncLlm
from .llms.chained import AsyncChainedLlm, ChainedLlm

from .types import Message, async_marked

from .data import Data, StructuredItem, resolve_data
from .prompting import SUMMARY_PROMPT, SYSTEM_PROMPT, get_prompt

from .utils import is_pydantic_model
from .models import Reasoned
from .fill import fill_dc


class _Aism:
    """(internal) Inner working aism."""

    __slots__ = ("llm",)

    llm: Union[AsyncLlm, SyncLlm]

    def __init__(
        self, llm: Union[AsyncLlm, SyncLlm, Sequence[AsyncLlm], Sequence[SyncLlm]], /
    ):
        if isinstance(llm, list):
            if isinstance(llm[0], AsyncLlm):
                self.llm = AsyncChainedLlm(llm)  # type: ignore
            else:
                self.llm = ChainedLlm(llm)  # type: ignore

        else:
            self.llm = llm  # type: ignore

    def give(
        self, *items: StructuredItem, label: Optional[str] = None
    ) -> "GiveSession":
        """Provide data with the LLM.

        ```python
        session = ai.give(...)
        ```
        """
        return GiveSession(self, *items, label=label)

    def is_async(self) -> bool:
        return async_marked(self.llm)

    def _rq(self, *, messages: Sequence[Message]) -> Any:
        """(internal) Create a request.

        Does not care if this is async/sync.
        """
        return self.llm.completion(messages=messages)


class GiveSession:
    """Give session (mutable)."""

    aism: _Aism
    data: MutableSequence[tuple[Sequence[Data], Optional[str]]]

    def __init__(
        self, aism: _Aism, *items: StructuredItem, label: Optional[str] = None
    ):
        self.aism = aism
        self.data = [(list(resolve_data(item) for item in items), label)]

    def _collect_data(self) -> str:
        s = "[DATA ONLY] [CONTEXT ONLY]\nBelow is the data:"

        for data, label in self.data:
            if label:
                s += f"\n\n* The below data rows is labeled: **{label}**"

            for n, data_row in enumerate(data):
                text = data_row.fmt()
                if "\n" in text:
                    p = "\n" + text.strip("\n ")
                else:
                    p = " " + text

                s += f"\n(data row {n}):{p}"

        return s

    # fill
    async def _awaited_fill(self, dc, messages):
        res = (await self.aism._rq(messages=messages)).strip("` ")
        result = rjsonc.loads(res)

        reasoning = result["reasoning"]

        if result.get("errors"):
            raise RuntimeError(
                f"failed to fill model {dc.__name__}, causes:\n● "
                + "\n● ".join(result["errors"])
            )

        if is_pydantic_model(dc):
            model = Reasoned(reasoning, dc.validate(result["model"]))
        else:
            model = Reasoned(reasoning, fill_dc(dc, result["model"]))

        return model

    def _sync_fill(self, dc, messages):
        res = self.aism._rq(messages=messages).strip("` ")
        result = rjsonc.loads(res)

        reasoning = result["reasoning"]

        if result.get("errors"):
            raise RuntimeError(
                f"failed to fill model {dc.__name__}, causes:\n● "
                + "\n● ".join(result["errors"])
            )

        if is_pydantic_model(dc):
            model = Reasoned(reasoning, dc.validate(result["model"]))
        else:
            model = Reasoned(reasoning, fill_dc(dc, result["model"]))

        return model

    def fill(self, dc: Any, /):
        """Fill a dataclass with the given data."""
        prompt = get_prompt(dc)

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {"role": "user", "content": self._collect_data()},
            {
                "role": "user",
                "content": "Below is the schema (format) you should be returning (// comments are allowed):\n"
                + prompt
                + "\nNote: You **must** return in the JSONC format with nothing else. "
                + "Your response should correspond to the data provided earlier."
                + "**All reasoning should be in the `reasoning` column or with `// comments`**. Do not add backticks (```).\n"
                + "Once you've added your reasoning in the `reasoning` column, if you found out that you cannot fill the model "
                + 'due to incomplete or non-inferrable data, instead of writing "model" and continue with filling, add a `errors` '
                + "column, with a list of reasons why this cannot be filled.\nExample of error:\n"
                + '  "errors": [\n'
                + '    "SomeModel.some_field: cannot ... due to ...",'
                + "    // ... more reasons"
                + "  ]",
            },
        ]

        if self.aism.is_async():
            return self._awaited_fill(dc, messages)
        else:
            return self._sync_fill(dc, messages)

    def prompt(self, s: str, /):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": self._collect_data()},
            {"role": "user", "content": s},
        ]
        return self.aism._rq(messages=messages)

    def describe(self, mode: Literal["concise", "summary"] = "summary"):
        """Describe the provided data."""
        return self.prompt(
            (
                SUMMARY_PROMPT
                if mode == "summary"
                else "Summarize the above data. Keep it concise."
            ),
        )

    # mentioned
    def _sync_mentioned(self, messages):
        res = self.aism._rq(messages=messages)
        mentioned = res.splitlines()[-1].strip(" .").lower()
        reasoning = res.splitlines()[:-1]

        if mentioned == "true":
            return Reasoned(reasoning, True)
        elif mentioned == "false":
            return Reasoned(reasoning, False)
        elif mentioned == "partial":
            return Reasoned(reasoning, "partial")
        else:
            raise ValueError(f"unknown 'mentioned' identifier: {mentioned!r}")

    async def _awaited_mentioned(self, messages):
        res = await self.aism._rq(messages=messages)
        mentioned = res.splitlines()[-1].strip(" .").lower()
        reasoning = res.splitlines()[:-1]

        if mentioned == "true":
            return Reasoned(reasoning, True)
        elif mentioned == "false":
            return Reasoned(reasoning, False)
        elif mentioned == "partial":
            return Reasoned(reasoning, "partial")
        else:
            raise ValueError(f"unknown 'mentioned' identifier: {mentioned!r}")

    def mentioned(self, snippet: str, /) -> Any:
        """Checks whether the snippet is mentioned."""
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": self._collect_data()},
            {
                "role": "user",
                "content": (
                    f"Given the above data, think about whether: {snippet!r} is mentioned. "
                    + "You may first add your thoughts to the response, however **the last line must be true/false/partial, lower case.** "
                    + "In other words, after your analyzed it, add a new line and write true if it's **mentioned** or **can be inferred**. "
                    + "If it is **completely unmentioned**, write false. If it's partially mentioned (not in a full scale), write partial."
                ),
            },
        ]
        if self.aism.is_async():
            return self._awaited_mentioned(messages)
        else:
            return self._sync_mentioned(messages)

    def compare(self, *, topic: Optional[str] = None):
        p = f" focused on the topic '{topic}'" if topic else ""
        return self.prompt(
            f"Compare all the data rows, and provide a brief summary{p} with Markdown of what the differences/similarities are."
        )

    def translate(self, to: str = "en") -> str:
        return self.prompt(f"Translate all the data rows to the language {to!r}.")

    # give

    def give(self, *items: StructuredItem, label: Optional[str] = None) -> Self:
        """Provide data with the LLM, chained.

        **Note**: `self` will mutate, extending elements from the provided items.

        ```python
        session = session.give(...)
        ```
        """
        self.data.append((list(resolve_data(item) for item in items), label))
        return self

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return exc_type is None

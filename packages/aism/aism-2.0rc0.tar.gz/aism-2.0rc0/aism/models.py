from dataclasses import dataclass
from typing import Annotated, Generic, TypeVar


T = TypeVar("T")


@dataclass
class Reasoned(Generic[T]):
    reasoning: Annotated[list[str], "Thoughts and reasoning"]
    model: T


@dataclass
class MentionedModel:
    mentioned: Annotated[
        bool,
        "true if it's **mentioned** or **can be inferred**",
        "false if it's **completely not mentioned** or **unknown**",
        "if it's partially mentioned, keep this false.",
    ]
    is_partial: Annotated[bool, "partially mentioned (not in a full scale)?"]

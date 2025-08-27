import dataclasses
from datetime import datetime as Datetime

from typing import Any, ClassVar, Literal, Optional, Protocol, Sequence, Union
from typing_extensions import TypedDict

Role = Union[str, Literal["user", "assistant", "system"]]


class _MessageDict(TypedDict):
    role: Role
    content: str


Message = Union[_MessageDict, dict[str, Any]]


class AsyncMarker:
    """Marks a class as async-based."""


def async_marked(obj: object) -> bool:
    """Checks whether an object is marked with `AsyncMarker`."""
    return isinstance(obj, AsyncMarker)


class PydanticModelLike(Protocol):
    __name__: str
    __pydantic_fields__: dict[str, "PydanticFieldInfoLike"]

    @staticmethod
    def validate(data) -> "PydanticModelLike": ...


class PydanticFieldInfoLike(Protocol):
    annotation: Optional[type[Any]]
    alias: Optional[str]
    description: Optional[str]

    def is_required(self) -> bool: ...


StructuredItem = Union[
    str,
    int,
    float,
    bool,
    Sequence["StructuredItem"],
    dict[str, "StructuredItem"],
    "StructuredDataclassInstance",
    "PydanticModelLike",
    Datetime,
]


class StructuredDataclassInstance(Protocol):
    __dataclass_fields__: ClassVar[dict[str, dataclasses.Field["StructuredItem"]]]

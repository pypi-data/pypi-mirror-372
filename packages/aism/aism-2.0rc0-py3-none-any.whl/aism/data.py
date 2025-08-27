import dataclasses
from datetime import datetime

from typing import Generic, TypeVar
from typing_extensions import Sequence

from .utils import is_pydantic_model
from .types import PydanticModelLike, StructuredItem, StructuredDataclassInstance


T = TypeVar("T", bound=StructuredItem)


class Data(Generic[T]):
    __slots__ = ("data",)

    def __init__(self, item: T):
        self.data = item

    def fmt(self) -> str: ...


class IntData(Data[int]):
    def fmt(self) -> str:
        return str(self.data)


class FloatData(Data[float]):
    def fmt(self) -> str:
        return str(self.data)


class StrData(Data[str]):
    def fmt(self) -> str:
        return self.data


class BoolData(Data[bool]):
    def fmt(self) -> str:
        return str(self.data)


class SequenceData(Data[Sequence[StructuredItem]]):
    def fmt(self) -> str:
        s = "(list)"

        for i, item in enumerate(self.data):
            d = resolve_data(item)
            s += "\n" + str(i) + ": " + d.fmt()

        return s


class DictData(Data[dict[str, StructuredItem]]):
    def fmt(self) -> str:
        s = "(key-value)"

        for key, value in self.data.items():
            s += "\n" + key + ": " + resolve_data(value).fmt()

        return s


class DataclassData(Data[StructuredDataclassInstance]):
    def fmt(self) -> str:
        s = "(key-value)"

        for field in self.data.__dataclass_fields__.values():
            key = field.name
            value = getattr(self, key)
            s += "\n" + key + ": " + resolve_data(value).fmt()

        return s


class PydanticModelData(Data[PydanticModelLike]):
    def fmt(self) -> str:
        s = "(key-value)"

        for name, field in self.data.__pydantic_fields__.items():
            value = getattr(self, name)
            s += "\n" + name + ": " + resolve_data(value).fmt()

        return s


class DatetimeData(Data[datetime]):
    def fmt(self) -> str:
        return self.data.strftime("%Y-%m-%d %H:%M:%S (%a)")


def resolve_data(data: StructuredItem) -> Data:
    if isinstance(data, bool):
        return BoolData(data)

    elif isinstance(data, int):
        return IntData(data)

    elif isinstance(data, float):
        return FloatData(data)

    elif isinstance(data, list) or isinstance(data, tuple):
        return SequenceData(data)

    elif isinstance(data, str):
        return StrData(data)

    elif isinstance(data, dict):
        return DictData(data)

    elif is_pydantic_model(data):
        return PydanticModelData(data)

    elif dataclasses.is_dataclass(data):
        return DataclassData(data)

    elif isinstance(data, datetime):
        return DatetimeData(data)

    else:
        raise NotImplementedError("unsupported type: " + repr(type(data)))

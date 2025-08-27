from dataclasses import is_dataclass
from typing import Annotated, Any, Callable, TypeVar, get_origin, get_type_hints

from .utils import is_pydantic_model
from .prompting import get_prompt

_Filler = Callable[[Any], Any]

_ZERO_FILLER = lambda x: x  # noqa


def get_filler(dt) -> _Filler:
    if dt in (bool, str, int, float):
        return _ZERO_FILLER

    if is_dataclass(dt):
        if hasattr(dt, "__aism_filler__"):
            return getattr(dt, "__aism_filler__")

        fillers = {}
        hints = get_type_hints(dt)
        for field in dt.__dataclass_fields__.values():
            fillers[field.name] = get_filler(hints[field.name])

        @staticmethod
        def fill(d):
            # captures: fillers
            kwargs = {}
            for name, filler in fillers.items():
                kwargs[name] = filler(d[name])
            return dt(**kwargs)  # type: ignore

        setattr(dt, "__aism_filler__", fill)

        return fill

    elif is_pydantic_model(dt):
        if hasattr(dt, "__aism_filler__"):
            return getattr(dt, "__aism_filler__")

        def fill_pydantic(d):
            return dt.validate(d)

        setattr(dt, "__aism_filler__", fill_pydantic)

        return fill_pydantic

    origin = get_origin(dt)
    if origin is list:
        filler = get_filler(dt.__args__[0])
        return lambda x: list(map(filler, x))
    elif origin is dict:
        filler = get_filler(dt.__args__[1])
        return lambda x: {k: filler(v) for k, v in x.items()}
    elif origin is Annotated:
        filler = get_filler(dt.__args__[0])
        return filler

    return _ZERO_FILLER


def fill_dc(dc, data: dict):
    """Fill a dataclass."""
    try:
        filler = get_filler(dc)
        return filler(data)

    except Exception as err:
        raise ValueError(f"failed to fill dataclass {dc.__name__}") from err


T = TypeVar("T")


def fillable(typ: type[T]) -> type[T]:
    """Create fillable contexts for a dataclass at startup time.

    Could be used as a decorator or a common function.

    ```python
    @fillable
    @dataclass
    class Person:
        name: str

    print(getattr(Person, "__aism_filler__"))
    print(getattr(Person, "__aism_prompt__"))
    ```
    """
    get_filler(typ)
    get_prompt(typ)
    return typ

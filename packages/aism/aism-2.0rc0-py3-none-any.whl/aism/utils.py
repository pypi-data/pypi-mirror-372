from typing_extensions import Never, TypeGuard

from .types import PydanticModelLike


class UnreachableError(Exception):
    """This item is not reachable."""


def unreachable(d: str = "arm", /) -> Never:
    """Marks all contents below (including the current line) unreachable.

    Args:
        d (str): Description of what's unreachable.
    """
    raise UnreachableError(f"unreachable {d}!")


def is_pydantic_model(obj) -> TypeGuard[PydanticModelLike]:
    return hasattr(obj, "__pydantic_fields__")


def fill_pydantic(p: PydanticModelLike, data: dict):
    """Fill a pydantic model."""
    return p.validate(data)

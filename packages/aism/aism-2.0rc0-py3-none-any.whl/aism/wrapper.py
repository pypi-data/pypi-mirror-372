from typing import TYPE_CHECKING

from ._aism import _Aism, GiveSession


if not TYPE_CHECKING:
    SyncSession = AsyncSession = GiveSession
    AsyncAism = Aism = _Aism

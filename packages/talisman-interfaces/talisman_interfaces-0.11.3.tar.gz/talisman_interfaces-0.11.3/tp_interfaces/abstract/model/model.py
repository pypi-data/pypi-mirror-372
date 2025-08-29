from typing import AsyncContextManager, Protocol

from typing_extensions import Self


class AsyncModel(AsyncContextManager[Self], Protocol):
    async def __aenter__(self) -> Self:
        return self

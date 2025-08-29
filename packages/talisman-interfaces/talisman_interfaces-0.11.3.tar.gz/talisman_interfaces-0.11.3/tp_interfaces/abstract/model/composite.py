from typing import AsyncContextManager, Generic, Iterable, TypeVar

from typing_extensions import Self

from .model import AsyncModel

_AsyncModel = TypeVar('_AsyncModel', bound=AsyncContextManager)


class AbstractAsyncCompositeModel(AsyncModel, Generic[_AsyncModel]):
    def __init__(self, models: Iterable[_AsyncModel]):
        self._models = tuple(models)

    async def __aenter__(self) -> Self:
        for m in self._models:
            await m.__aenter__()
        return self

    async def __aexit__(self, __exc_type, __exc_value, __traceback):
        for m in self._models[::-1]:
            await m.__aexit__(__exc_type, __exc_value, __traceback)

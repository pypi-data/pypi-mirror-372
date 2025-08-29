from abc import ABCMeta, abstractmethod
from typing import Generic, Type, TypeVar

from .update import AbstractUpdate, UpdateMode
from ..model import AsyncModel

_Update = TypeVar('_Update', bound=AbstractUpdate)


class AbstractUpdatableModel(AsyncModel, Generic[_Update]):

    async def update(self, update: _Update) -> None:
        if update.mode is UpdateMode.add:
            await self._add(update)
        else:
            await self._remove(update)

    @abstractmethod
    async def _add(self, update: _Update) -> None:
        pass

    @abstractmethod
    async def _remove(self, update: _Update) -> None:
        pass

    @property
    @abstractmethod
    def update_type(self) -> Type[_Update]:
        pass


class UpdatableModelMixin(AbstractUpdatableModel[_Update], Generic[_Update], metaclass=ABCMeta):
    def __init__(self, model: AbstractUpdatableModel):
        self._model = model

    async def update(self, update: _Update) -> None:
        await self._model.update(update)

    async def _add(self, update: _Update) -> None:
        await self._model._add(update)

    async def _remove(self, update: _Update) -> None:
        await self._model._remove(update)

    @property
    def update_type(self) -> Type[_Update]:
        return self._model.update_type

from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar

from typing_extensions import Self

from tp_interfaces.abstract.model import AsyncModel

_Model = TypeVar('_Model', bound=AsyncModel)


class AbstractModelWrapper(AsyncModel, Generic[_Model], metaclass=ABCMeta):
    def __init__(self, model: _Model, **kwargs):
        self._model = model

    async def __aenter__(self) -> Self:
        await self._model.__aenter__()
        return self

    async def __aexit__(self, *exc):
        await self._model.__aexit__(*exc)

    @classmethod
    def from_config(cls, model: _Model, config: dict) -> Self:
        kwargs = cls.parse_config(config)
        return cls(model, **kwargs)

    @staticmethod
    @abstractmethod
    def parse_config(config: dict) -> dict:
        pass

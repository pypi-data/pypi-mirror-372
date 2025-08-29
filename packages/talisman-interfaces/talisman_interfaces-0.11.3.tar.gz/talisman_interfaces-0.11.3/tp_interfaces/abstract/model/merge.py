from abc import ABCMeta, abstractmethod
from typing import Protocol, TypeVar, runtime_checkable

from typing_extensions import Self

from .model import AsyncModel

_Model = TypeVar('_Model', bound=AsyncModel, covariant=True)


@runtime_checkable
class MergeModel(Protocol[_Model]):

    @abstractmethod
    def can_be_merged(self, model: _Model) -> bool:
        ...

    @abstractmethod
    def merge(self, model: _Model) -> Self:
        ...


class IDBasedMergeModel(MergeModel, metaclass=ABCMeta):

    def can_be_merged(self, model: AsyncModel) -> bool:
        if isinstance(model, IDBasedMergeModel):
            return self.id == model.id
        return False

    @property
    @abstractmethod
    def id(self) -> str:
        pass

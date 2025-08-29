from abc import ABCMeta, abstractmethod
from typing import Generic, Iterable, Type, TypeVar

from typing_extensions import Self

_DataType = TypeVar('_DataType')


class AbstractDataModel(Generic[_DataType], metaclass=ABCMeta):

    @classmethod
    @abstractmethod
    def serialize(cls, data: _DataType) -> Self:
        ...

    @abstractmethod
    def deserialize(self) -> _DataType:
        ...

    @classmethod
    @abstractmethod
    def data_type(cls) -> Type[_DataType]:
        ...


def get_serializer(serializers: Iterable[Type[AbstractDataModel]], data_type: Type[_DataType]) -> Type[AbstractDataModel[_DataType]]:
    for serializer in serializers:
        if issubclass(data_type, serializer.data_type()):
            return serializer

    raise ValueError(f"No serializer found for {data_type}")

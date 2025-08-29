from abc import ABCMeta
from typing import Protocol, Type, TypeVar, runtime_checkable

from tdm import TalismanDocument

from tp_interfaces.abstract.processor import AbstractProcessor
from tp_interfaces.abstract.schema import ImmutableBaseModel
from tp_interfaces.serializable import Serializable

_Config = TypeVar('_Config', bound=ImmutableBaseModel)


@runtime_checkable
class AbstractDocumentProcessor(AbstractProcessor[_Config, TalismanDocument, TalismanDocument], Protocol[_Config]):

    @property
    def config_type(self) -> Type[_Config]:
        raise NotImplementedError

    @property
    def input_type(self) -> Type[TalismanDocument]:
        return TalismanDocument

    @property
    def output_type(self) -> Type[TalismanDocument]:
        return TalismanDocument


class AbstractSerializableDocumentProcessor(AbstractDocumentProcessor, Serializable, metaclass=ABCMeta):
    pass

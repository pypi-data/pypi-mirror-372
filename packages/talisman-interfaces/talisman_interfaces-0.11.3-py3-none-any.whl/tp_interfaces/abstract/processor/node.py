from abc import ABCMeta, abstractmethod
from functools import partial
from typing import Generic, Iterable, Iterator, Type, TypeVar

from tdm import TalismanDocument
from tdm.abstract.datamodel import AbstractNode

from tp_interfaces.abstract.schema import ImmutableBaseModel
from .processor import AbstractDocumentProcessor

_Config = TypeVar('_Config', bound=ImmutableBaseModel)
_Node = TypeVar('_Node', bound=AbstractNode)


class AbstractNodeProcessor(AbstractDocumentProcessor, Generic[_Config, _Node], metaclass=ABCMeta):
    """
    A base abstract processor for processing document nodes.
    """

    async def process_doc(self, document: TalismanDocument, config: _Config) -> TalismanDocument:
        filter_node = partial(self._filter_node, document=document)
        nodes = document.get_nodes(type_=self._node_type, filter_=filter_node)
        return document.with_nodes(self._process_nodes(nodes, config=config))

    def _filter_node(self, node: _Node, document: TalismanDocument) -> bool:
        return True

    @property
    def _node_type(self) -> Type[_Node]:
        return AbstractNode

    @abstractmethod
    def _process_node(self, node: _Node, config: _Config) -> _Node:
        pass

    def _process_nodes(self, nodes: Iterable[_Node], config: _Config) -> Iterator[_Node]:
        return map(partial(self._process_node, config=config), nodes)

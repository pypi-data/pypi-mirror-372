from abc import ABCMeta
from collections import defaultdict
from typing import Callable, Generic, Iterable, Iterator, Optional, Type, TypeVar

from tdm.abstract.datamodel import AbstractNode

from tp_interfaces.abstract.schema import ImmutableBaseModel
from .node import AbstractNodeProcessor
from .processor import AbstractDocumentProcessor
from .. import AbstractAsyncCompositeModel

_Config = TypeVar('_Config', bound=ImmutableBaseModel)
_Category = TypeVar('_Category')

_Node = TypeVar('_Node', bound=AbstractNode)


class AbstractCategoryAwareNodeProcessor(
    AbstractAsyncCompositeModel[AbstractNodeProcessor[_Config, _Node]],
    AbstractNodeProcessor[_Config, _Node],
    Generic[_Config, _Node, _Category],
    metaclass=ABCMeta
):
    def __init__(
            self,
            category2processor: dict[_Category, AbstractNodeProcessor[_Config, _Node]],
            categorizer: Callable[[_Node], _Category],
            default_processor: Optional[AbstractDocumentProcessor[_Config]] = None
    ):
        self._category2processor = dict(category2processor)
        super().__init__(self._category2processor.values())
        self._models: tuple[AbstractDocumentProcessor[_Config], ...]
        self._categorizer = categorizer
        self._default = default_processor

    def _process_node(self, node: _Node, config: _Config) -> _Node:
        return next(self._process_nodes([node], config))

    def _process_nodes(self, nodes: Iterable[_Node], config: _Config) -> Iterator[_Node]:
        category2node = defaultdict(list)

        for node in nodes:
            category = self._categorizer(node)
            category2node[category].append(node)

        for category, nodes in category2node.items():
            processor = self._category2processor.get(category, self._default)
            if processor is None:
                raise ValueError(f"No processor registered for {category} (available categories: {list(self._category2processor)})")
            yield from processor._process_nodes(nodes, config)

    @property
    def config_type(self) -> Type[_Config]:
        return self._models[0].config_type

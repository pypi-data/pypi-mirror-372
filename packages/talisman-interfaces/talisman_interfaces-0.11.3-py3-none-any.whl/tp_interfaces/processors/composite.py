import logging
import operator
from operator import attrgetter
from typing import Iterable, Sequence, Type, TypeVar

from pydantic import BaseModel, ValidationError, create_model
from tdm import TalismanDocument

from tp_interfaces.abstract import AbstractDocumentProcessor, ImmutableBaseModel
from tp_interfaces.abstract.model.composite import AbstractAsyncCompositeModel
from tp_interfaces.abstract.model.merge import MergeModel
from tp_interfaces.logging.time import AsyncTimeMeasurer

logger = logging.getLogger(__name__)

_Config = TypeVar('_Config', bound=BaseModel)


class SequentialConfig(ImmutableBaseModel):
    pass


class SequentialDocumentProcessor(
    AbstractAsyncCompositeModel[AbstractDocumentProcessor],
    AbstractDocumentProcessor[SequentialConfig]
):

    def __init__(self, processors: Iterable[tuple[str, AbstractDocumentProcessor]]):
        processors = tuple(processors)
        AbstractAsyncCompositeModel[AbstractDocumentProcessor].__init__(self, map(operator.itemgetter(1), processors))
        AbstractDocumentProcessor.__init__(self)

        self._config_type = None
        self._config_extractors = ()
        self._model_names = tuple(map(operator.itemgetter(0), processors))

    async def __aenter__(self):
        await AbstractAsyncCompositeModel.__aenter__(self)

        config_extractors = []
        config_types = {}
        nonempty_idx = None
        for idx, (model_name, model) in enumerate(zip(self._model_names, self._models)):
            if not model.config_type.model_fields:
                config = model.config_type()
                config_extractors.append(lambda _, config=config: config)  # use hack (config=config) to fix Late Binding Closures
                continue
            if model_name in config_types:
                raise ValueError(f"duplicate model name {model_name}")
            try:
                default_config = model.config_type()
            except ValidationError:
                default_config = ...
            config_types[model_name] = (model.config_type, default_config)
            config_extractors.append(attrgetter(model_name))
            nonempty_idx = idx

        if len(config_types) == 1:
            config_extractors[nonempty_idx] = lambda config: config
            self._config_type = next(iter(config_types.values()))[0]
        else:
            if any(not name for name in config_types):
                raise ValueError(f"empty model name couldn't be processed")
            self._config_type = create_model('RuntimeSequentialConfig', **config_types, __base__=SequentialConfig)

        self._config_extractors = tuple(config_extractors)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await AbstractAsyncCompositeModel.__aexit__(self, exc_type, exc_val, exc_tb)
        self._config_type = None
        self._config_extractors = ()

    async def process_doc(self, document: TalismanDocument, config: SequentialConfig) -> TalismanDocument:
        return (await self.process_docs([document], config))[0]

    async def process_docs(
            self,
            documents: Sequence[TalismanDocument],
            config: SequentialConfig
    ) -> tuple[TalismanDocument, ...]:
        for processor, config_extractor in zip(self._models, self._config_extractors):
            async with AsyncTimeMeasurer(f"processing {len(documents)} documents with {processor}", logger=logger):
                documents = await processor.process_docs(documents, config_extractor(config))
        return documents

    @property
    def config_type(self) -> Type[SequentialConfig]:
        if self._config_type is None:
            raise RuntimeError('First call the __aenter__ method!')
        return self._config_type

    @classmethod
    def build(cls, processors: Iterable[tuple[str, AbstractDocumentProcessor]], *, merge: bool = True) -> AbstractDocumentProcessor:
        processors = tuple(cls._merge_models(processors)) if merge else tuple(processors)
        if len(processors) == 1:
            return processors[0][1]
        return SequentialDocumentProcessor(processors)

    @staticmethod
    def _merge_models(models: Iterable[tuple[str, AbstractDocumentProcessor]]) -> Iterable[tuple[str, AbstractDocumentProcessor]]:
        current_merger: MergeModel | None = None
        merger_name: str | None = None
        for name, model in models:
            if current_merger is not None:
                if current_merger.can_be_merged(model):
                    current_merger = current_merger.merge(model)
                else:
                    yield merger_name, current_merger
                    merger_name, current_merger = None, None
            if current_merger is None:
                if isinstance(model, MergeModel):
                    merger_name, current_merger = name, model
                else:
                    yield name, model
        if current_merger is not None:
            yield merger_name, current_merger

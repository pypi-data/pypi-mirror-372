from operator import attrgetter
from typing import Generic, Iterable, Optional, Tuple, Type, TypeVar

from pydantic import create_model

from tp_interfaces.abstract import AbstractDocumentProcessor, AbstractUpdatableModel, AbstractUpdate, UpdateMode
from tp_interfaces.processors.composite import SequentialDocumentProcessor

_Update = TypeVar('_Update', bound=AbstractUpdate)


class SequentialUpdate(AbstractUpdate):
    mode: Optional[UpdateMode] = None


class UpdatableSequentialDocumentProcessor(AbstractUpdatableModel[_Update], SequentialDocumentProcessor, Generic[_Update]):

    def __init__(self, processors: Iterable[Tuple[str, AbstractDocumentProcessor]]):
        super().__init__(processors)

        update_types = {}
        update_config_extractors = []

        for model_name, model in zip(self._model_names, self._models):
            if not isinstance(model, AbstractUpdatableModel):
                continue
            if model_name in update_types:
                raise ValueError(f"duplicate model name {model_name}")
            update_types[model_name] = (model.update_type, None)
            update_config_extractors.append(attrgetter(model_name))

        if len(update_types) == 1:
            self._update_type = update_types.popitem()[1][0]
            self._update_config_extractors = (lambda config: config,)
        elif any(not name for name in update_types):
            raise ValueError(f"empty model name couldn't be processed")
        else:
            self._update_type = create_model('RuntimeSequentialUpdate', **update_types, __base__=SequentialUpdate)
            self._update_config_extractors = tuple(update_config_extractors)

    @property
    def update_type(self) -> Type[_Update]:
        return self._update_type

    async def update(self, update: _Update) -> None:
        filtered = filter(lambda x: isinstance(x, AbstractUpdatableModel), self._models)
        for processor, update_config_extractor in zip(filtered, self._update_config_extractors):
            sub_update = update_config_extractor(update)

            if sub_update:
                await processor.update(sub_update)

    async def _add(self, update: _Update) -> None:
        raise NotImplementedError

    async def _remove(self, update: _Update) -> None:
        raise NotImplementedError

    @classmethod
    def build(cls, processors: Iterable[Tuple[str, AbstractDocumentProcessor]], *,
              merge: bool = True) -> AbstractDocumentProcessor:
        processors = tuple(cls._merge_models(processors)) if merge else tuple(processors)
        if len(processors) == 1:
            return processors[0][1]

        if any(isinstance(processor[1], AbstractUpdatableModel) for processor in processors):
            return UpdatableSequentialDocumentProcessor(processors)

        return SequentialDocumentProcessor(processors)

import random
import string
from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar

from pydantic import ConfigDict, create_model

from tp_interfaces.abstract import AbstractDocumentProcessor, AbstractModelWrapper, ImmutableBaseModel

_Processor = TypeVar('_Processor', bound=AbstractDocumentProcessor)


class WrapperConfig(ImmutableBaseModel):
    def get_processor_config(self) -> ImmutableBaseModel:
        raise NotImplementedError

    model_config = ConfigDict(extra='allow')


_WrapperConfig = TypeVar('_WrapperConfig', bound=WrapperConfig)


class AbstractProcessorWrapper(AbstractModelWrapper[_Processor], Generic[_Processor, _WrapperConfig], metaclass=ABCMeta):

    async def __aenter__(self):
        await super().__aenter__()
        self._config_type = await self._generate_runtime_config()
        return self

    @abstractmethod
    async def _generate_runtime_config(self):
        pass

    @staticmethod
    def _generate_wrapper_config(
        base_config: type[_WrapperConfig],
        model_config: type[ImmutableBaseModel],
        check_intersection: bool = True
    ) -> type[_WrapperConfig]:
        base_fields = base_config.model_fields
        model_fields = model_config.model_fields

        intersection = set(model_fields).intersection(base_fields)
        if check_intersection and intersection:
            raise TypeError(f'filter and model field names collision: {intersection}')

        class _RuntimeConfig(base_config):
            def get_processor_config(self) -> model_config:
                return model_config(**{f: getattr(self, f) for f in model_fields})

        result = create_model(
            f'{base_config.__name__}_{model_config.__name__}_{_id()}',
            __base__=_RuntimeConfig,
            **{name: (field_info.annotation, field_info) for name, field_info in model_fields.items() if name not in base_fields}
        )

        return result


def _id(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

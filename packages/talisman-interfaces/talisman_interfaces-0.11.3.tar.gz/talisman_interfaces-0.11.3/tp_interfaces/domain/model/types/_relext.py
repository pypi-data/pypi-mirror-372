from dataclasses import dataclass

from tp_interfaces.domain.abstract import AbstractRelExtBasedType, RelExtModel


@dataclass(frozen=True)
class RelExtBasedType(AbstractRelExtBasedType):
    _pretrained_relext_models: tuple[RelExtModel, ...] = tuple()

    def __post_init__(self):
        if self._pretrained_relext_models:
            object.__setattr__(self, '_pretrained_relext_models', tuple(map(self._convert_to_model, self._pretrained_relext_models)))
        elif isinstance(self._pretrained_relext_models, list):
            object.__setattr__(self, '_pretrained_relext_models', tuple(self._pretrained_relext_models))

    @property
    async def pretrained_relext_models(self) -> tuple[RelExtModel, ...]:
        return self._pretrained_relext_models

    @staticmethod
    def _convert_to_model(obj) -> RelExtModel:
        if isinstance(obj, RelExtModel):
            return obj
        if isinstance(obj, dict):
            return RelExtModel(**obj)
        raise ValueError

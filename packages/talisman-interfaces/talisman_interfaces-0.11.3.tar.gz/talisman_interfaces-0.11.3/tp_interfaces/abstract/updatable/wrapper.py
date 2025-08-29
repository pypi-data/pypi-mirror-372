from abc import ABCMeta
from typing import Generic, TypeVar

from tp_interfaces.abstract.model import AbstractModelWrapper
from .model import AbstractUpdatableModel, UpdatableModelMixin
from .update import AbstractUpdate

_Update = TypeVar('_Update', bound=AbstractUpdate)


class UpdatableModelWrapper(
    AbstractModelWrapper[AbstractUpdatableModel[_Update]],
    UpdatableModelMixin[_Update], Generic[_Update],
    metaclass=ABCMeta
):
    """
    Utility class that creates either updatable extractor wrapper (if wrapped model is updatable) or general extractor wrapper.
    Note: this class subclasses should not override `from_config` method (AbstractModelWrapper `from_config` should be used)
    """

    def __init__(self, model: AbstractUpdatableModel[_Update], *args, **kwargs):
        AbstractModelWrapper[AbstractUpdatableModel[_Update]].__init__(self, model)
        if not isinstance(model, AbstractUpdatableModel):
            raise ValueError
        UpdatableModelMixin.__init__(self, model)

    @classmethod
    def from_config(cls, model: AbstractUpdatableModel, config: dict):
        if isinstance(model, AbstractUpdatableModel):
            kwargs = cls.parse_config(config)
            return cls(model, **kwargs)
        return cls.__base__.from_config(model, config)

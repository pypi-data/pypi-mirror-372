from typing import Protocol, TypeVar

_Model = TypeVar('_Model', covariant=True)


class AbstractConfigConstructableModel(Protocol[_Model]):
    @classmethod
    def from_config(cls, config: dict) -> _Model:
        ...

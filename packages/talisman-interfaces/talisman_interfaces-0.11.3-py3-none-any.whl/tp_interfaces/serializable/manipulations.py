from pathlib import Path
from typing import Type, TypeVar, Union

from tp_interfaces.serializable.abstract import Serializable
from tp_interfaces.serializable.directory_mixin import DirectorySerializableMixin
from tp_interfaces.serializable.pickle_mixin import PicklableMixin

_Serializable = TypeVar('_Serializable', bound=Union[Serializable, PicklableMixin])


def load_object(path: Path, *, expected_class: Type[_Serializable] = Serializable) -> _Serializable:
    if path.is_dir():
        model = DirectorySerializableMixin.load(path)
    else:
        model = PicklableMixin.load(path)
    if not isinstance(model, expected_class):
        raise TypeError(f'Expected {expected_class.__name__} at {path} but loaded {model.__class__.__name__}!')
    return model

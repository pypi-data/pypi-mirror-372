import inspect
import json
import time
from abc import ABCMeta
from importlib import import_module
from pathlib import Path
from typing import Any, Callable, Optional

from typing_extensions import Self

from tp_interfaces.serializable.abstract import Serializable

INFO_FILE = 'info.json'
CONFIG_FILE = 'config.json'


def load_info_file(directory: Path, *, default: Optional[dict] = None) -> dict:
    info_file = directory / INFO_FILE

    if info_file.exists():
        with info_file.open('r', encoding='utf-8') as f:
            return json.load(f)

    if default is None:
        raise ValueError(f'File {INFO_FILE} is missing from {directory} and no default value is provided for info!')

    return default


def _get_constructor_param_values(target_type: type):
    """
    get target type constructor parameter values

    @param target_type: type of the created object
    @return: mapping from parameter name to its value (except self)
    """
    frame = inspect.currentframe().f_back  # get caller frame
    caller_class = None
    names = tuple(inspect.signature(target_type.__init__).parameters)
    # unlovely replacement for inspect.f_code.co_qualname below:
    while caller_class is not target_type:
        frame = frame.f_back
        current_local_types = {type(v) for v in frame.f_locals.values()}
        if target_type in current_local_types and frame.f_code.co_names[1] == "__init__" \
                and set(names).issubset(set(frame.f_locals.keys())):
            caller_class = type(frame.f_locals['self'])

    return {
        name: frame.f_locals[name] for name in names[1:]  # skip self
    }


class DirectorySerializableMixin(Serializable, metaclass=ABCMeta):
    """
    Mixin class that implements basic directory serialization and deserialization.
    This mixin should be initialized in serializable object constructor to collect actual parameters.

    This mixin stores initial constructor parameter values and serializes them.
    Object will be created with the same parameters while deserialization.

    Make sure that superclass constructors do not mutate their arguments and that there is no name collision
    in the variables of child and parent classes which descend from this mixin. An illustration of these failure modes
    can be seen in tp_interfaces_tests/serializable/serializable.py
    """

    CREATED_INFO_FIELD = 'created'
    CLASS_INFO_FIELD = 'class'
    EXTERNAL_PARAMETERS = 'external'

    def __init__(self):
        params = _get_constructor_param_values(type(self))
        self._inline_config: dict[str, Any] = {}
        self._serializable: dict[str, tuple[Any, Callable, Callable]] = {}
        for name, value in params.items():
            try:
                # check if class specifies special method for current value serialization/deserialization
                serializer, deserializer = self._serializer(value)
                self._serializable[name] = value, serializer, deserializer
            except ValueError:
                # if not, assume value is json-serializable
                self._inline_config[name] = value

    @classmethod
    def load(cls, path: Path) -> Self:
        if not path.exists():
            raise ValueError(f'Path {path} does not exist!')

        if not path.is_dir():
            raise ValueError(f'Provided path {path} is not a directory!')

        info = load_info_file(path)
        class_name: str = info.get(cls.CLASS_INFO_FIELD)
        if class_name is None:
            raise ValueError(f'Broken info file: there is no {cls.CLASS_INFO_FIELD} field value')
        try:
            module, name = class_name.rsplit('.', 1)
            module = import_module(module)
            cls_ = getattr(module, name)
        except Exception as e:
            raise ImportError(f"Couldn't import {class_name} class", e)
        if not isinstance(cls_, type):
            raise TypeError(f"{class_name} is not a class")
        if not issubclass(cls_, cls):
            raise TypeError(f"Expected class {cls.__name__} at {path} but found {cls_.__name__}!")

        return cls_._load_from_directory(path, info=info)

    @classmethod
    def _load_from_directory(cls, directory_path: Path, info: dict) -> Self:
        with (directory_path / CONFIG_FILE).open('r', encoding='utf-8') as f:
            params = json.load(f)
        if not isinstance(params, dict):
            raise ValueError
        params: dict
        for param, deserializer in info.get(cls.EXTERNAL_PARAMETERS, {}).items():
            module = import_module(deserializer['module'])
            if deserializer.get('class') is not None:
                module = getattr(module, deserializer['class'])
            func = getattr(module, deserializer['name'])
            params[param] = func(directory_path / param)
        return cls(**params)

    def _get_info(self) -> dict:
        def build_config(deserializer: dict | Callable) -> dict:
            if isinstance(deserializer, dict):
                return deserializer
            qualname = deserializer.__qualname__
            if '.' in qualname:
                class_name, name = qualname.rsplit('.', 1)
            else:
                class_name, name = None, qualname
            return {
                "module": inspect.getmodule(deserializer).__name__,
                "class": class_name,
                "name": name
            }

        return {
            self.CREATED_INFO_FIELD: time.strftime("%Y-%m-%d %H:%M"),
            self.CLASS_INFO_FIELD: f'{self.__class__.__module__}.{self.__class__.__name__}',
            self.EXTERNAL_PARAMETERS: {
                name: build_config(deserializer) for name, (_, _, deserializer) in self._serializable.items()
            },
            **self._get_extra_info()
        }

    def _get_extra_info(self) -> dict:
        return {}

    def save(self, path: Path, *, rewrite: bool = False) -> None:
        self._create_empty_dir(path, clear=rewrite)

        info_file = path / INFO_FILE
        info = self._get_info()
        with info_file.open('w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        return self._save_to_directory(path)

    def _save_to_directory(self, directory_path: Path) -> None:
        with (directory_path / CONFIG_FILE).open('w', encoding='utf-8') as f:
            json.dump(self._inline_config, f, ensure_ascii=False, indent=2)
        for param, (value, serializer, _) in self._serializable.items():
            serializer(value, directory_path / param)

    @classmethod
    def _serializer(cls, obj) -> tuple[Callable[[Any, Path], None], Callable[[Path], Any] | dict]:
        """
        get special serialization/deserialization methods for object

        @param obj: object to be serialized
        @return: serialization function and deserialization function (or its specification: module, class and method name)
        """
        if isinstance(obj, Serializable):
            return lambda o, p: o.save(p), obj.load
        from tp_interfaces.serializable import DictWrapper
        if isinstance(obj, DictWrapper):
            return DictWrapper.save, DictWrapper.load
        raise ValueError

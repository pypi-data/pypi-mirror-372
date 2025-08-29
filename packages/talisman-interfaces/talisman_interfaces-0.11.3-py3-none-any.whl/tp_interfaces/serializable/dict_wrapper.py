import inspect
from functools import wraps
from pathlib import Path

from typing_extensions import Self

from tp_interfaces.serializable.abstract import Serializable
from tp_interfaces.serializable.manipulations import load_object


class DictWrapper(dict[str, Serializable]):
    def __init__(self, content: dict[str, Serializable]):
        dict.__init__(self, content)

    @classmethod
    def load(cls, path: Path) -> Self:
        content = {}
        for file in path.glob("*"):
            content[file.name] = load_object(file)
        return cls(content)

    def save(self, path: Path, *, rewrite: bool = False) -> None:
        for name, item in self.items():
            item.save(path / name)

    @classmethod
    def convert_dict(cls, param: str):
        def wrapper(f):
            signature = inspect.signature(f)

            @wraps(f)
            def wrap(*args, **kwargs):
                bound_args = signature.bind(*args, **kwargs)
                bound_args.apply_defaults()
                named_args = bound_args.arguments
                named_args[param] = cls(named_args[param])
                return f(**named_args)

            return wrap

        return wrapper

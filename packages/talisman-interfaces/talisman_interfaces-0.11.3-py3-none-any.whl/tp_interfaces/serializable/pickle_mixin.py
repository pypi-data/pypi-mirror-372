import pickle
from pathlib import Path
from typing import TypeVar

from typing_extensions import Self

from tp_interfaces.serializable.abstract import Serializable

_T = TypeVar('_T', bound='PicklableMixin')


def read_dvc_bytes(path: Path) -> bytes:
    import dvc.api
    # problem with dvc.api.open: https://github.com/iterative/dvc/issues/4667
    return dvc.api.read(str(path.with_suffix('')), mode='rb')


class PicklableMixin(Serializable):

    @classmethod
    def load(cls, path: Path) -> Self:
        if path.suffix == '.dvc':
            model = pickle.loads(read_dvc_bytes(path))
        else:
            with path.open('rb') as f:
                model = pickle.load(f)
        if not isinstance(model, cls):
            raise pickle.PickleError(f"Pickled object at {path} is not an instance of {cls.__name__} class.")
        return model

    def save(self, path: Path, *, rewrite: bool = False) -> None:
        if path.exists() and not rewrite:
            raise Exception(f"Saving path exists: {path}")
        self._create_empty_dir(path.parent)

        with path.open('wb') as f:
            pickle.dump(self, f, protocol=5)  # fixed protocol version to avoid issues with serialization on Python 3.10+ versions

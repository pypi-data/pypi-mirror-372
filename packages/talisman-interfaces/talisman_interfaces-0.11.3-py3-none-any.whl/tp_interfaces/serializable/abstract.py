import os
import shutil
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import TypeVar

from typing_extensions import Self

_T = TypeVar('_T', bound='Serializable')


class Serializable(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def load(cls, path: Path) -> Self:
        pass

    @abstractmethod
    def save(self, path: Path, *, rewrite: bool = False) -> None:
        pass

    @staticmethod
    def _create_empty_dir(directory: Path, *, clear: bool = False) -> None:
        if directory.exists():
            if not directory.is_dir():
                raise ValueError(f'Provided path {directory} is not a directory!')
            if clear:
                shutil.rmtree(directory)

        os.makedirs(directory, exist_ok=True)

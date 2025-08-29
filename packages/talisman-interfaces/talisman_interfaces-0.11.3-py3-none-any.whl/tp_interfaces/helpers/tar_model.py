import os
import tarfile
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Callable, Dict, IO, TypeVar, Union


def create_tar_wrapper(names2paths: Dict[str, Union[Path, str]]) -> bytes:
    """
    Function tars single file with arcname "model" and return bytes buffer with it
    """
    if not names2paths:
        raise ValueError("No directories given for tar!")

    bytes_buffer = BytesIO()
    with tarfile.open(mode="w:", fileobj=bytes_buffer) as tar:
        for name, path in names2paths.items():
            if isinstance(path, str):
                path = Path(path)
            if not os.path.isdir(path):
                raise NotADirectoryError(f'Path \'{path}\' not a directory')

            tar.add(path, arcname=name)
    return bytes_buffer.getvalue()


_T = TypeVar('_T')


def extract_tar(tared_model: IO[bytes], extractor: Callable[[Path], _T]) -> _T:
    """
    Extracts all tarred files into temporary directory and applies extractor
    """
    with tarfile.open("r:", fileobj=tared_model) as tar:
        with tempfile.TemporaryDirectory() as dir_name:
            tar.extractall(dir_name)
            return extractor(Path(dir_name))

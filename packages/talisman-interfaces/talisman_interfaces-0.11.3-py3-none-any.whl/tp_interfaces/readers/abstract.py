import asyncio
from abc import ABC, ABCMeta, abstractmethod
from pathlib import Path
from typing import Any, AsyncIterator, Dict, Iterator, Type, TypeVar

from tdm import TalismanDocument

from tp_interfaces.helpers.io import check_path_existence

_AbstractConfigurableReader = TypeVar('_AbstractConfigurableReader', bound='AbstractConfigurableReader')


class AbstractPathConstructor(metaclass=ABCMeta):
    @abstractmethod
    def get_data_paths(self, filepath: Path) -> Iterator[Any]:
        pass


class OneFilePathConstructor(AbstractPathConstructor):
    def get_data_paths(self, filepath: Path) -> Iterator[Dict[str, Path]]:
        yield {'filepath': Path(filepath)}


class MultiFilePathConstructor(AbstractPathConstructor):
    def __init__(self, pattern: str = "*"):
        self._pattern = pattern

    def get_data_paths(self, filepath: Path) -> Iterator[Dict[str, Path]]:
        check_path_existence(filepath)
        for path_doc in filepath.glob(self._pattern):
            yield {'filepath': Path(path_doc)}


class _FakeAsyncIterator(AsyncIterator[TalismanDocument]):

    def __init__(self, sync_iterator: Iterator[TalismanDocument]):
        self._iterator = sync_iterator

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            await asyncio.sleep(0)  # switch coroutine
            return next(self._iterator)
        except StopIteration:
            raise StopAsyncIteration


class AbstractReader(metaclass=ABCMeta):
    def __init__(self, filepath: Path):
        self._filepath = filepath

    @abstractmethod
    def read_doc(self, *args, **kwargs) -> Iterator[TalismanDocument]:
        pass

    async def aread_doc(self, *args, **kwargs) -> AsyncIterator[TalismanDocument]:
        return _FakeAsyncIterator(self.read_doc(*args, **kwargs))  # TODO: implement async read methods

    def read(self) -> Iterator[TalismanDocument]:
        for path_config in self.path_constructor.get_data_paths(self._filepath):
            for doc in self.read_doc(**path_config):
                yield doc

    async def aread(self) -> AsyncIterator[TalismanDocument]:
        for path_config in self.path_constructor.get_data_paths(self._filepath):
            async for doc in await self.aread_doc(**path_config):
                yield doc

    @property
    def path_constructor(self) -> AbstractPathConstructor:
        return OneFilePathConstructor()


class AbstractConfigurableReader(AbstractReader, metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def from_config(cls: _AbstractConfigurableReader, config) -> _AbstractConfigurableReader:
        pass


def replace_path_constructor(reader_type: Type[AbstractReader], path_constructor) -> Type[AbstractReader]:
    class WrappedReaderClass(reader_type, ABC):
        @property
        def path_constructor(self) -> AbstractPathConstructor:
            return path_constructor

    return WrappedReaderClass

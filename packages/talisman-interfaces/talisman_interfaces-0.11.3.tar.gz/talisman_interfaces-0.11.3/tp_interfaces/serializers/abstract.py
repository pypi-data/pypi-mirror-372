from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import AsyncIterator, Iterable, TextIO

from tdm import TalismanDocument
from typing_extensions import Protocol


class AsyncTextIO(Protocol):
    @property
    def closed(self) -> bool:
        ...

    async def writable(self) -> bool:
        ...

    async def write(self, b: str, /) -> int:
        ...


class AbstractSerializer(metaclass=ABCMeta):
    @abstractmethod
    def serialize(self, doc: TalismanDocument, stream: TextIO):
        pass

    @abstractmethod
    async def aserialize(self, doc: TalismanDocument, stream: AsyncTextIO):
        pass

    @staticmethod
    def _check_stream(stream: TextIO):
        if stream.closed or not stream.writable():
            raise Exception("stream  is closed or not writeable")

    @staticmethod
    async def _a_check_stream(stream: AsyncTextIO):
        if stream.closed or not await stream.writable():
            raise Exception("stream  is closed or not writeable")


class AbstractPathSerializer(metaclass=ABCMeta):
    @abstractmethod
    def serialize(self, docs: Iterable[TalismanDocument], path: Path):
        pass

    @abstractmethod
    async def aserialize(self, docs: AsyncIterator[TalismanDocument], path: Path):
        pass

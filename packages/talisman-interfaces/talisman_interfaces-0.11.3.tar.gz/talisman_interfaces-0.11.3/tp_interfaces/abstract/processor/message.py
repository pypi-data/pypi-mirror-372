import time
import uuid
from dataclasses import dataclass
from typing import Protocol, Type, TypeVar, runtime_checkable

from typing_extensions import Self

from tp_interfaces.abstract.processor import AbstractProcessor
from tp_interfaces.abstract.schema import ImmutableBaseModel

_Config = TypeVar('_Config', bound=ImmutableBaseModel)


@dataclass(frozen=True, init=False)
class File:
    path: str
    filename: str
    checksum: str

    def __init__(self, path: str, filename: str, checksum: str, **kwargs):
        object.__setattr__(self, "path", path)
        object.__setattr__(self, "filename", filename)
        object.__setattr__(self, "checksum", checksum)
        for key, value in kwargs.items():
            object.__setattr__(self, key, value)


@dataclass(frozen=True, init=False)
class Message:
    id: str
    timestamp: int
    file: File | None
    parent_uuid: str | None

    def __init__(
            self,
            id_: str | None = None,
            file: File | None = None,
            parent_uuid: str | None = None,
            timestamp: int | None = None,
            **kwargs
    ):
        object.__setattr__(self, "id", id_ if id_ else str(uuid.uuid1()))
        object.__setattr__(self, "timestamp", timestamp if timestamp else int(time.time()))
        object.__setattr__(self, "file", file)
        object.__setattr__(self, "parent_uuid", parent_uuid)
        for key, value in kwargs.items():
            object.__setattr__(self, key, value)

    @classmethod
    def create(
            cls,
            parent_uuid: str | None = None,
            s3_path: str | None = None,
            file_hash: str | None = None,
            file_name: str | None = None,
            file_fields: dict | None = None,
            fields: dict | None = None
    ) -> Self:
        file_fields = {} if file_fields is None else file_fields
        fields = {} if fields is None else fields
        file = File(path=s3_path, checksum=file_hash, filename=file_name, **file_fields) if s3_path else None
        message = Message(parent_uuid=parent_uuid, file=file, **fields)
        return message


@runtime_checkable
class AbstractMessageProcessor(AbstractProcessor[_Config, Message, Message], Protocol[_Config]):

    @property
    def config_type(self) -> Type[_Config]:
        raise NotImplementedError

    @property
    def input_type(self) -> Type[Message]:
        return Message

    @property
    def output_type(self) -> Type[Message]:
        return Message

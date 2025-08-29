from enum import Enum

from tp_interfaces.abstract.schema import ImmutableBaseModel


class UpdateMode(str, Enum):  # `str` is needed for correct JSON schema generation
    add = 'add'
    remove = 'remove'


class AbstractUpdate(ImmutableBaseModel):
    mode: UpdateMode

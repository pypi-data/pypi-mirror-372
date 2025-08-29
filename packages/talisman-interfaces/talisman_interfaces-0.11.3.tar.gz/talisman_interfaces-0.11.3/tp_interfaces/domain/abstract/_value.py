from abc import ABCMeta
from dataclasses import dataclass
from typing import Optional

from tdm.datamodel.domain import AtomValueType

from ._nerc import AbstractNERCBasedType


@dataclass(frozen=True)
class AbstractLiteralValueType(AbstractNERCBasedType, AtomValueType, metaclass=ABCMeta):
    value_restriction: Optional[tuple[str, ...]] = None

    def __post_init__(self):
        AtomValueType.__post_init__(self)
        if isinstance(self.value_restriction, list):
            object.__setattr__(self, 'value_restriction', tuple(self.value_restriction))

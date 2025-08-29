from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Optional

from tdm.abstract.datamodel.domain import AbstractDomainType


@dataclass(frozen=True)
class RelExtModel(object):
    relation_type: str
    invert_direction: bool = False
    source_annotation: Optional[str] = None
    target_annotation: Optional[str] = None


class AbstractRelExtBasedType(AbstractDomainType, metaclass=ABCMeta):
    @property
    @abstractmethod
    async def pretrained_relext_models(self) -> tuple[RelExtModel, ...]:
        pass

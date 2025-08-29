from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Optional

from tdm.abstract.datamodel.domain import AbstractDomainType


@dataclass(frozen=True)
class NERCRegexp(object):
    regexp: str
    context_regexp: Optional[str] = None
    auto_create: bool = False


class AbstractNERCBasedType(AbstractDomainType, metaclass=ABCMeta):

    @property
    @abstractmethod
    async def regexp(self) -> tuple[NERCRegexp, ...]:
        pass

    @property
    @abstractmethod
    async def black_regexp(self) -> tuple[NERCRegexp, ...]:
        pass

    @property
    @abstractmethod
    async def pretrained_nerc_models(self) -> tuple[str, ...]:
        pass

    @property
    @abstractmethod
    async def dictionary(self) -> tuple[str, ...]:
        pass

    @property
    @abstractmethod
    async def black_list(self) -> tuple[str, ...]:
        pass

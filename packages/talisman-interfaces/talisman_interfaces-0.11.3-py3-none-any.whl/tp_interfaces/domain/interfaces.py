from abc import ABCMeta, abstractmethod
from typing import AsyncContextManager, Iterable

from tdm.abstract.datamodel import AbstractDomain
from typing_extensions import Self


class AbstractDomainChangeHook(object):
    @abstractmethod
    def __call__(self, domain: AbstractDomain) -> None:
        pass

    @classmethod
    @abstractmethod
    def from_config(cls, config: dict) -> Self:
        pass


class DomainProducer(AsyncContextManager, metaclass=ABCMeta):
    def __init__(self, hooks: Iterable[AbstractDomainChangeHook] = tuple()):
        self._hooks: list[AbstractDomainChangeHook] = list(hooks)

    @abstractmethod
    async def has_changed(self) -> bool:
        pass

    async def get_domain(self) -> AbstractDomain:
        domain = await self._get_domain()
        for hook in self._hooks:
            hook(domain)
        return domain

    @abstractmethod
    async def _get_domain(self) -> AbstractDomain:
        pass

    def register_hook(self, hook: AbstractDomainChangeHook) -> None:
        self._hooks.append(hook)

    @classmethod
    @abstractmethod
    def from_config(cls, config: dict) -> Self:
        pass

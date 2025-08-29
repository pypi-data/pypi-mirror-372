from asyncio import Lock
from typing import Optional

from tdm.abstract.datamodel import AbstractDomain

from tp_interfaces.domain.interfaces import DomainProducer


class _Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


lock = Lock()


class DomainManager(metaclass=_Singleton):
    def __init__(self):
        self._factory: Optional[DomainProducer] = None
        self._domain = None

        self._entered = 0

    def __bool__(self):
        return self._factory is not None

    def set_producer(self, domain_factory: DomainProducer) -> None:
        if self._entered:
            raise AttributeError("Domain producer is already in use")
        self._factory = domain_factory

    def del_producer(self):
        if self._entered:
            raise AttributeError("Domain producer is already in use")
        self._factory = None

    async def __aenter__(self):
        if self._factory is None:
            raise ValueError("No domain producer is set")
        async with lock:
            if not self._entered:
                await self._factory.__aenter__()
                self._domain = await self._factory.get_domain()
            self._entered += 1
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        async with lock:
            self._entered -= 1
            if not self._entered:
                await self._factory.__aexit__(exc_type, exc_val, exc_tb)
                self._domain = None

    @property
    async def has_changed(self) -> bool:
        async with lock:
            return await self._has_changed()

    @property
    async def domain(self) -> AbstractDomain:
        async with lock:
            has_changed = await self._has_changed()
            while has_changed:
                self._domain = await self._factory.get_domain()
                has_changed = await self._has_changed()
            return self._domain

    async def _has_changed(self) -> bool:
        if not self._entered:
            raise AttributeError
        return await self._factory.has_changed()

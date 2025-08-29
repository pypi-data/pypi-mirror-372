from tdm.abstract.datamodel import AbstractDomain
from tdm.datamodel.domain import Domain
from typing_extensions import Self

from tp_interfaces.domain.interfaces import DomainProducer
from tp_interfaces.domain.model import DomainModel

EMPTY_DOMAIN = Domain(())


class StubDomainProducer(DomainProducer):
    def __init__(self, domain: AbstractDomain = EMPTY_DOMAIN):
        super().__init__()
        self._domain = domain

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        pass

    async def has_changed(self) -> bool:
        return False

    async def _get_domain(self) -> AbstractDomain:
        return self._domain

    @classmethod
    def from_config(cls, config: dict) -> Self:
        """Config example:
        {
            "domain": {
                ...`KBSchema` config...
            }
        }
        """
        return cls(domain=DomainModel.model_validate(config['domain']).deserialize())

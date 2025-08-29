from tdm.abstract.datamodel import AbstractDomain
from tdm.datamodel.domain import set_default_domain
from typing_extensions import Self

from tp_interfaces.domain.interfaces import AbstractDomainChangeHook


class SetDefaultDomainHook(AbstractDomainChangeHook):
    def __call__(self, domain: AbstractDomain) -> None:
        set_default_domain(domain)

    @classmethod
    def from_config(cls, config: dict) -> Self:
        return cls()

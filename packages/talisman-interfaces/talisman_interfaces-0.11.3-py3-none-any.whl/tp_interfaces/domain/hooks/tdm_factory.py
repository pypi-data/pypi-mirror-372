from tdm import TalismanDocumentModel
from tdm.abstract.datamodel import AbstractDomain
from typing_extensions import Self

from tp_interfaces.domain.interfaces import AbstractDomainChangeHook


class UpdateTDMDefaultDomainHook(AbstractDomainChangeHook):
    def __call__(self, domain: AbstractDomain) -> None:
        TalismanDocumentModel.set_default_domain(domain)

    @classmethod
    def from_config(cls, config: dict) -> Self:
        return cls()

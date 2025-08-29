from pydantic import BaseModel
from tdm.abstract.datamodel import AbstractDomain
from tdm.datamodel.domain import Domain

from ._types_registry import DomainTypesModel


class DomainModel(BaseModel):
    types: DomainTypesModel

    def deserialize(self) -> Domain:
        return Domain(self.types.deserialize({}))

    @classmethod
    def serialize(cls, domain: AbstractDomain) -> 'DomainModel':
        return cls(
            types=DomainTypesModel.serialize(domain.types)
        )

from abc import ABCMeta
from dataclasses import dataclass, field

from tdm.abstract.datamodel import FactStatus
from tdm.datamodel.domain import PropertyType, RelationPropertyType
from tdm.datamodel.facts import ConceptFact, PropertyFact, ValueFact

from ._nerc import AbstractNERCBasedType
from ._relext import AbstractRelExtBasedType


@dataclass(frozen=True)
class AbstractPropertyType(AbstractRelExtBasedType, PropertyType, metaclass=ABCMeta):
    isIdentifying: bool = field(init=False, default=False)  # noqa N815

    def build_fact(self, status: FactStatus, source: ConceptFact, target: ValueFact) -> PropertyFact:
        return PropertyFact(status, self, source, target)


@dataclass(frozen=True)
class AbstractIdentifyingPropertyType(AbstractNERCBasedType, PropertyType, metaclass=ABCMeta):
    isIdentifying: bool = field(init=False, default=True)  # noqa N815


class AbstractRelationPropertyType(AbstractRelExtBasedType, RelationPropertyType, metaclass=ABCMeta):
    pass

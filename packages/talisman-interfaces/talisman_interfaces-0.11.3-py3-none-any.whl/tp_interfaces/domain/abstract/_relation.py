from abc import ABCMeta

from tdm.abstract.datamodel import FactStatus
from tdm.datamodel.domain import RelationType
from tdm.datamodel.facts import ConceptFact, RelationFact

from ._relext import AbstractRelExtBasedType


class AbstractRelationType(AbstractRelExtBasedType, RelationType, metaclass=ABCMeta):
    def build_fact(self, status: FactStatus, source: ConceptFact, target: ConceptFact) -> RelationFact:
        return RelationFact(status, self, source, target)

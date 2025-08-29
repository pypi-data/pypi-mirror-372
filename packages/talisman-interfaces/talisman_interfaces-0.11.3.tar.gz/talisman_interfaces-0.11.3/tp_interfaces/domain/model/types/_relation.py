from dataclasses import dataclass

from tdm.abstract.json_schema import generate_model

from tp_interfaces.domain.abstract import AbstractRelationType
from ._concept import ConceptType
from ._relext import RelExtBasedType

__deps = (ConceptType,)


@generate_model(label='relation')
@dataclass(frozen=True)
class RelationType(RelExtBasedType, AbstractRelationType):

    def __post_init__(self):
        RelExtBasedType.__post_init__(self)
        AbstractRelationType.__post_init__(self)

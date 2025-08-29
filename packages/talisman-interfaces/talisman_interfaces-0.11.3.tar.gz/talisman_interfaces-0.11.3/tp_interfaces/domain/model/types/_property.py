from dataclasses import dataclass

from tdm.abstract.json_schema import generate_model

from tp_interfaces.domain.abstract import AbstractIdentifyingPropertyType, AbstractPropertyType, AbstractRelationPropertyType
from ._concept import ConceptType
from ._nerc import NERCBasedType
from ._relation import RelationType
from ._relext import RelExtBasedType
from ._value import AtomValueType

__deps = (AtomValueType, ConceptType, RelationType)


@generate_model(label='property')
@dataclass(frozen=True)
class PropertyType(RelExtBasedType, AbstractPropertyType):

    def __post_init__(self):
        RelExtBasedType.__post_init__(self)
        AbstractPropertyType.__post_init__(self)


@generate_model(label='id_property')
@dataclass(frozen=True)
class IdentifyingPropertyType(NERCBasedType, AbstractIdentifyingPropertyType):

    def __post_init__(self):
        NERCBasedType.__post_init__(self)
        AbstractIdentifyingPropertyType.__post_init__(self)


@generate_model(label='r_property')
@dataclass(frozen=True)
class RelationPropertyType(RelExtBasedType, AbstractRelationPropertyType):
    def __post_init__(self):
        RelExtBasedType.__post_init__(self)
        AbstractRelationPropertyType.__post_init__(self)

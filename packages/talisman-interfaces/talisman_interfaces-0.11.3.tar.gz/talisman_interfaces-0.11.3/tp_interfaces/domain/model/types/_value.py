from dataclasses import dataclass

from tdm.abstract.json_schema import generate_model
from tdm.datamodel.domain import CompositeValueType

from tp_interfaces.domain.abstract import AbstractLiteralValueType
from ._nerc import NERCBasedType


@generate_model(label='atom')
@dataclass(frozen=True)
class AtomValueType(NERCBasedType, AbstractLiteralValueType):

    def __post_init__(self):
        NERCBasedType.__post_init__(self)
        AbstractLiteralValueType.__post_init__(self)


generate_model(label='composite')(CompositeValueType)

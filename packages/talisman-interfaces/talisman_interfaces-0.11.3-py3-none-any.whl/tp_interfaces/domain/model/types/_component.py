from dataclasses import dataclass

from tdm.abstract.json_schema import generate_model

from tp_interfaces.domain.abstract import AbstractComponentValueType
from ._relext import RelExtBasedType
from ._value import AtomValueType

__deps = (AtomValueType,)


@generate_model(label='component')
@dataclass(frozen=True)
class ComponentValueType(RelExtBasedType, AbstractComponentValueType):
    pass

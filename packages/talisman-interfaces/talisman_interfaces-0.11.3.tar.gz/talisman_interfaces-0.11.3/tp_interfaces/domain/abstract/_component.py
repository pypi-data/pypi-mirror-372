from abc import ABCMeta

from tdm.datamodel.domain import ComponentValueType

from ._relext import AbstractRelExtBasedType


class AbstractComponentValueType(AbstractRelExtBasedType, ComponentValueType, metaclass=ABCMeta):
    pass

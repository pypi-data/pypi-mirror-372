from typing import Type

from tdm.abstract.datamodel import AbstractDomainType
from tdm.abstract.json_schema import AbstractLabeledModel, ModelsGenerator, get_model_generator
from tdm.abstract.json_schema.decorator import _MODELS_GENERATORS


def register_domain_types_models() -> Type[AbstractLabeledModel]:
    _MODELS_GENERATORS[AbstractDomainType] = ModelsGenerator(AbstractDomainType)
    import tp_interfaces.domain.model.types as types
    types

    # TODO: here plugin for extra domain types

    return get_model_generator(AbstractDomainType).generate_labeled_model('DomainTypesModel')


DomainTypesModel = register_domain_types_models()

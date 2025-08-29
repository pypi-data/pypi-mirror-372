from tdm.abstract.json_schema import generate_model
from tdm.datamodel.domain import ConceptType
from tdm.datamodel.domain.types import DocumentType

generate_model(label='concept')(ConceptType)
generate_model(label='document')(DocumentType)

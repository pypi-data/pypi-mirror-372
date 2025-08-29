from tdm.abstract.datamodel import AbstractDomainType


def get_id(type_id: str | AbstractDomainType) -> str:
    """
    Utility function that extracts str type_id.
    """
    if isinstance(type_id, str):
        return type_id
    return type_id.id  # noqa: AbstractDomainType is EnsureIdentifiable

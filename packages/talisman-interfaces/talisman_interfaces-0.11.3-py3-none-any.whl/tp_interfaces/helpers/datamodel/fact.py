from functools import singledispatch
from typing import Iterator

from tdm import TalismanDocument
from tdm.abstract.datamodel import AbstractFact
from tdm.datamodel.facts import AtomValueFact, ComponentFact, CompositeValueFact, ConceptFact, MentionFact, PropertyFact, RelationFact


def get_document_facts(doc: TalismanDocument) -> Iterator[AbstractFact]:
    """Yield all information about document fact(with id = doc.id)"""
    try:
        doc_fact = doc.get_fact(doc.id)
    except KeyError:
        return

    yield doc_fact
    for prop in doc.get_facts(PropertyFact, filter_=PropertyFact.source_filter(ConceptFact.id_filter(doc.id))):
        yield prop
        yield from get_value(prop.target, doc)

    for relation in doc.get_facts(RelationFact, filter_=RelationFact.source_filter(ConceptFact.id_filter(doc.id))):
        yield relation
        yield relation.target


@singledispatch
def get_value(value: AbstractFact, doc: TalismanDocument) -> Iterator[AbstractFact]:
    """Recursively retrieves all dependencies for a value fact (mentions, components)."""
    raise NotImplementedError


@get_value.register
def _(value: AtomValueFact, doc: TalismanDocument) -> Iterator[AbstractFact]:
    yield value
    yield from doc.related_facts(value, MentionFact)


@get_value.register
def _(value: CompositeValueFact, doc: TalismanDocument) -> Iterator[AbstractFact]:
    yield value
    for component in doc.related_facts(value, ComponentFact):
        yield component
        yield from get_value(component.target, doc)

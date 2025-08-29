from collections import defaultdict
from typing import Iterable

from tdm.abstract.datamodel import AbstractFact, AbstractNode, AbstractNodeMention, FactStatus
from tdm.datamodel.domain import AtomValueType, ConceptType, PropertyType, RelationType
from tdm.datamodel.facts import AtomValueFact, ConceptFact, MentionFact, PropertyFact, RelationFact
from tdm.datamodel.mentions import TextNodeMention
from tdm.datamodel.nodes import TableCellNode, TableCellNodeMetadata, TableNode, TableRowNode, TextNode


def generate_concept_facts(
        cpt_type: str | ConceptType,
        props: dict[str | PropertyType, tuple[str | AtomValueType, TextNode | AbstractNodeMention]],
        relations: dict[str | RelationType, Iterable[AbstractFact]] = None,
        status: FactStatus = FactStatus.NEW
) -> list[AbstractFact]:
    if relations is None:
        relations = {}
    result = []
    cpt = ConceptFact(status, cpt_type)
    result.append(cpt)
    for prop_type, (value_type, value_mention) in props.items():
        value, mention = generate_atom_value_facts(value_type, value_mention, status)
        result.extend([value, mention, PropertyFact(status, prop_type, cpt, value)])
    for rel_type, (target, *other) in relations.items():
        result.append(target)
        result.append(RelationFact(status, rel_type, cpt, target))
        result.extend(other)
    return result


def generate_atom_value_facts(
        value_type: str | AtomValueType, mention: TextNode | AbstractNodeMention, status: FactStatus = FactStatus.NEW
) -> tuple[AtomValueFact, MentionFact]:
    if isinstance(mention, TextNode):
        mention = TextNodeMention(mention, 0, len(mention.content))
    value = AtomValueFact(status, value_type)
    mention = MentionFact(status, mention, value)
    return value, mention


def generate_table_nodes(
        table: Iterable[Iterable[str]],
        vertical: bool = True,
        header_numbers: tuple[int, ...] = (0,)
) -> tuple[TableNode, dict[AbstractNode, Iterable[AbstractNode]], tuple[tuple[TextNode, ...], ...]]:
    root: TableNode = TableNode()
    structure: dict[AbstractNode, list[AbstractNode]] = defaultdict(list)
    cells: list[list[TextNode]] = []

    for i, row in enumerate(table):
        row_node = TableRowNode()
        structure[root].append(row_node)
        row_nodes = []
        for j, cell in enumerate(row):
            cell_node = TableCellNode(metadata=TableCellNodeMetadata(header=((i if vertical else j) in header_numbers)))
            structure[row_node].append(cell_node)
            text_node = TextNode(cell)
            structure[cell_node].append(text_node)
            if vertical or j != 0:
                row_nodes.append(text_node)
        if i != 0 or not vertical:
            cells.append(row_nodes)

    return root, structure, tuple(tuple(row) for row in cells)

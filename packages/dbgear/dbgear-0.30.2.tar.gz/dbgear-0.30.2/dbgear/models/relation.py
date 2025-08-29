import pydantic

from .base import BaseSchema
from .notes import Note
from .notes import NoteManager


class EntityInfo(BaseSchema):
    schema_name: str
    table_name: str


class BindColumn(BaseSchema):
    source_column: str
    target_column: str


class Relation(BaseSchema):
    """Represents a relationship between two tables"""
    target: EntityInfo
    bind_columns: list[BindColumn]  # List of columns that bind the source and target
    cardinarity_source: str = '1'  # '1', '0..1', '0..*', '1..*'
    cardinarity_target: str = '1'  # '1', '0..1', '0..*', '1..*'

    # Physical foreign key constraint information
    constraint_name: str | None = None  # FK constraint name
    on_delete: str = "RESTRICT"  # CASCADE, SET NULL, SET DEFAULT, RESTRICT, NO ACTION
    on_update: str = "RESTRICT"  # CASCADE, SET NULL, SET DEFAULT, RESTRICT, NO ACTION
    deferrable: bool = False     # Whether the constraint is deferrable
    initially_deferred: bool = False  # Whether the constraint is initially deferred
    match_type: str = "SIMPLE"   # SIMPLE, FULL, PARTIAL (PostgreSQL)

    # Logical relationship information
    relationship_type: str = "association"  # association, composition, aggregation
    description: str | None = None  # Human-readable description of the relationship

    notes_: list[Note] = pydantic.Field(default_factory=list, alias='notes')

    @property
    def notes(self) -> NoteManager:
        return NoteManager(self.notes_)


class RelationManager:

    def __init__(self, relations: list[Relation]):
        self.relations = relations

    def __getitem__(self, index: int) -> Relation:
        return self.relations[index]

    def __iter__(self):
        yield from self.relations

    def __len__(self) -> int:
        return len(self.relations)

    def append(self, relation: Relation) -> None:
        self.relations.append(relation)

    def remove(self, relation: Relation) -> None:
        self.relations.remove(relation)

import pydantic

from .base import BaseSchema
from .notes import Note
from .notes import NoteManager


class Index(BaseSchema):
    index_name: str
    columns: list[str]
    index_type: str = "BTREE"  # BTREE, HASH, FULLTEXT, SPATIAL, etc.
    unique: bool = False
    partial_condition: str | None = None  # WHERE clause for partial indexes (PostgreSQL)
    include_columns: list[str] | None = None  # INCLUDE columns (PostgreSQL)
    storage_parameters: dict[str, str] | None = None  # Storage parameters
    tablespace: str | None = None  # Tablespace name

    notes_: list[Note] = pydantic.Field(default_factory=list, alias='notes')

    @property
    def notes(self) -> NoteManager:
        return NoteManager(self.notes_)


class IndexManager:

    def __init__(self, indexes: list[Index]):
        self.indexes = indexes

    def __getitem__(self, index: int) -> Index:
        return self.indexes[index]

    def __iter__(self):
        yield from self.indexes

    def __len__(self) -> int:
        return len(self.indexes)

    def append(self, index: Index) -> None:
        self.indexes.append(index)

    def remove(self, index: Index) -> None:
        self.indexes.remove(index)

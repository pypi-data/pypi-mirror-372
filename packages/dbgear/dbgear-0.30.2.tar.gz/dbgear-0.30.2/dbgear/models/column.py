import pydantic

from .base import BaseSchema
from .column_type import ColumnType
from .notes import Note
from .notes import NoteManager


class Column(BaseSchema):
    column_name: str
    display_name: str
    column_type: ColumnType  # Column type is now always a ColumnType object
    nullable: bool
    primary_key: int | None = None
    default_value: str | None = None

    # Column expression support
    expression: str | None = None  # Generated column expression
    stored: bool = False          # STORED/VIRTUAL distinction
    auto_increment: bool = False  # AUTO_INCREMENT attribute
    charset: str | None = None    # Character set for string columns
    collation: str | None = None  # Collation for string columns

    notes_: list[Note] = pydantic.Field(default_factory=list, alias='notes')

    @property
    def notes(self) -> NoteManager:
        return NoteManager(self.notes_)


class ColumnManager:

    def __init__(self, columns: list[Column]):
        self.columns = columns

    def __getitem__(self, key: int | str) -> Column:
        if isinstance(key, str):
            # Find column by name
            for column in self.columns:
                if column.column_name == key:
                    return column
            raise KeyError(f"Column '{key}' not found")
        elif isinstance(key, int):
            return self.columns[key]

        raise TypeError("list indices must be an integer or string")

    def __iter__(self):
        yield from self.columns

    def __len__(self) -> int:
        return len(self.columns)

    def append(self, column: Column) -> None:
        self.columns.append(column)

    def remove(self, column: Column) -> None:
        self.columns.remove(column)

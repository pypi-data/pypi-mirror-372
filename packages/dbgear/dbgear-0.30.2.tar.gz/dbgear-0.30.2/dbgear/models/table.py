import pydantic

from .base import BaseSchema
from .column import Column
from .column import ColumnManager
from .index import Index
from .index import IndexManager
from .relation import Relation
from .relation import RelationManager
from .notes import Note
from .notes import NoteManager


class MySQLTableOptions(BaseSchema):
    """MySQL-specific table options"""
    # ストレージエンジン
    engine: str = "InnoDB"  # InnoDB, MyISAM, MEMORY, etc.

    # 文字セット・照合順序
    charset: str | None = None  # utf8mb4, latin1, etc.
    collation: str | None = None  # utf8mb4_unicode_ci, etc.

    # AUTO_INCREMENT
    auto_increment: int | None = None  # 開始値

    # 行フォーマット
    row_format: str | None = None  # DYNAMIC, COMPRESSED, REDUNDANT, COMPACT

    # パーティション（MySQL）
    partition_by: str | None = None  # RANGE, LIST, HASH, KEY
    partition_expression: str | None = None
    partition_count: int | None = None  # HASH/KEY用のパーティション数


class Table(BaseSchema):
    table_name: str = pydantic.Field(exclude=True)
    display_name: str
    columns_: list[Column] = pydantic.Field(default_factory=list, alias='columns')
    indexes_: list[Index] = pydantic.Field(default_factory=list, alias='indexes')
    relations_: list[Relation] = pydantic.Field(default_factory=list, alias='relations')
    notes_: list[Note] = pydantic.Field(default_factory=list, alias='notes')

    # MySQL固有のテーブルオプション
    mysql_options: MySQLTableOptions | None = None

    @property
    def columns(self) -> ColumnManager:
        return ColumnManager(self.columns_)

    @property
    def indexes(self) -> IndexManager:
        return IndexManager(self.indexes_)

    @property
    def relations(self) -> RelationManager:
        return RelationManager(self.relations_)

    @property
    def notes(self) -> NoteManager:
        return NoteManager(self.notes_)


class TableManager:

    def __init__(self, tables: dict[str, Table]):
        self.tables = tables

    def __getitem__(self, table_name: str) -> Table:
        return self.tables[table_name]

    def __iter__(self):
        yield from self.tables.values()

    def __len__(self) -> int:
        return len(self.tables)

    def __contains__(self, table_name: str) -> bool:
        return table_name in self.tables

    def append(self, table: Table) -> None:
        if table.table_name in self.tables:
            raise ValueError(f"Table '{table.table_name}' already exists")
        self.tables[table.table_name] = table

    def remove(self, table_name: str) -> None:
        if table_name not in self.tables:
            raise KeyError(f"Table '{table_name}' not found")
        del self.tables[table_name]

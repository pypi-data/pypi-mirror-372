import pydantic
import yaml
import os

from .base import BaseSchema
from .column_type import ColumnType
from .column_type import ColumnTypeRegistry
from .table import Table
from .table import TableManager
from .view import View
from .view import ViewManager
from .trigger import Trigger
from .trigger import TriggerManager
from .procedure import Procedure
from .procedure import ProcedureManager
from .notes import Note
from .notes import NoteManager
from ..utils.populate import auto_populate_from_keys


class Schema(BaseSchema):
    name: str = pydantic.Field(exclude=True)
    tables_: dict[str, Table] = pydantic.Field(default_factory=dict, alias='tables')
    views_: dict[str, View] = pydantic.Field(default_factory=dict, alias='views')
    triggers_: dict[str, Trigger] = pydantic.Field(default_factory=dict, alias='triggers')
    procedures_: dict[str, Procedure] = pydantic.Field(default_factory=dict, alias='procedures')
    notes_: list[Note] = pydantic.Field(default_factory=list, alias='notes')

    @property
    def tables(self) -> TableManager:
        return TableManager(self.tables_)

    @property
    def views(self) -> ViewManager:
        return ViewManager(self.views_)

    @property
    def triggers(self) -> TriggerManager:
        return TriggerManager(self.triggers_)

    @property
    def procedures(self) -> ProcedureManager:
        return ProcedureManager(self.procedures_)

    @property
    def notes(self) -> NoteManager:
        return NoteManager(self.notes_)

    def merge(self, other):
        self.tables_.update(other.tables_)
        self.views_.update(other.views_)
        self.triggers_.update(other.triggers_)
        self.procedures_.update(other.procedures_)
        self.notes_.extend(other.notes_)


class SchemaManager(BaseSchema):
    schemas: dict[str, Schema] = {}
    registry_: dict[str, ColumnType] = pydantic.Field(default_factory=dict, alias='registry')
    notes_: list[Note] = pydantic.Field(default_factory=list, alias='notes')

    @classmethod
    def load(cls, filename: str):
        if not os.path.exists(filename):
            return None
        with open(filename, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        populated_data = auto_populate_from_keys(data, {
            'schemas.$1.name': '$1',
            'schemas.$1.tables.$2.instance': '$1',
            'schemas.$1.tables.$2.table_name': '$2',
            'schemas.$1.views.$2.instance': '$1',
            'schemas.$1.views.$2.view_name': '$2',
            'schemas.$1.triggers.$2.instance': '$1',
            'schemas.$1.triggers.$2.trigger_name': '$2',
            'schemas.$1.procedures.$2.instance': '$1',
            'schemas.$1.procedures.$2.procedure_name': '$2',
        })
        return cls(**populated_data)

    def save(self, filename: str) -> None:
        with open(filename, 'w', encoding='utf-8') as f:
            yaml.dump(
                self.model_dump(
                    by_alias=True,
                    exclude_none=True,
                    exclude_defaults=True
                ),
                f,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False)

    def __getitem__(self, name: str) -> Schema:
        return self.schemas[name]

    def __iter__(self):
        yield from self.schemas.values()

    def __len__(self) -> int:
        return len(self.schemas)

    def __contains__(self, name: str) -> bool:
        return name in self.schemas

    def append(self, schema: Schema) -> None:
        if schema.name in self.schemas:
            raise ValueError(f"Schema '{schema.name}' already exists")
        self.schemas[schema.name] = schema

    def remove(self, name: str) -> None:
        if name not in self.schemas:
            raise KeyError(f"Schema '{name}' not found")
        del self.schemas[name]

    @property
    def registry(self) -> ColumnTypeRegistry:
        return ColumnTypeRegistry(self.registry_)

    @property
    def notes(self) -> NoteManager:
        return NoteManager(self.notes_)

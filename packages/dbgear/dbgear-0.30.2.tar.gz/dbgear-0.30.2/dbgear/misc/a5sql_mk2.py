"""
A5:SQL Mk-2 (.a5er) file importer.

This module imports database schema definitions from A5:SQL Mk-2 files
and converts them to DBGear's native schema format.
"""

import csv
from dataclasses import dataclass
from dataclasses import field

from dbgear.models.schema import SchemaManager
from dbgear.models.schema import Schema
from dbgear.models.table import Table
from dbgear.models.column import Column
from dbgear.models.index import Index
from dbgear.models.notes import Note
from dbgear.models.column_type import parse_column_type
from dbgear.models.relation import Relation, EntityInfo, BindColumn


@dataclass
class Entity:
    instance: str = None
    table_name: str = None
    display_name: str = None
    fields: list = field(default_factory=list)
    indexes: list = field(default_factory=list)


@dataclass
class A5ERRelation:
    entity1: str = None
    entity2: str = None
    fields1: str = None
    fields2: str = None


@dataclass
class A5ERComment:
    comment: str = None
    page: str = None


class Parser:

    def __init__(self, mapping):
        self.mode = None
        self.mapping = mapping
        self.instances = {}
        self.relations = {}
        self.comments = []
        self.session = None

    def parse_line(self, line_no, line):
        if line == '':
            if self.mode == 2:
                if self.session.instance is not None:
                    if self.session.instance not in self.instances:
                        self.instances[self.session.instance] = []
                    self.instances[self.session.instance].append(self.session)
            if self.mode == 3:
                if self.session.entity2 not in self.relations:
                    self.relations[self.session.entity2] = {}
                for fld in self.session.fields2.split(','):
                    self.relations[self.session.entity2][fld] = self.session
            if self.mode == 4:
                if self.session.comment is not None:
                    self.comments.append(self.session)
            # 空行の場合、セッション解除
            self.mode = None
            return
        if line[0] == '#':
            return
        if self.mode is not None:
            name, value = self.split(line)
            if self.mode == 1:
                # 何もしない
                pass
            elif self.mode == 2:
                self.parse_entity(name, value)
            elif self.mode == 3:
                self.parse_relation(name, value)
            elif self.mode == 4:
                self.parse_comment(name, value)
            elif self.mode == 5:
                # 図形や線分オブジェクト（何もしない）
                pass
            else:
                raise RuntimeError(f'Unknown Mode: {self.mode}')
        else:
            if line == '[Manager]':
                self.mode = 1
            elif line == '[Entity]':
                self.mode = 2
                self.session = Entity()
            elif line == '[Relation]':
                self.mode = 3
                self.session = A5ERRelation()
            elif line == '[Comment]':
                self.mode = 4
                self.session = A5ERComment()
            elif line == '[Line]':
                self.mode = 5
            elif line == '[Shape]':
                self.mode = 5
            else:
                raise RuntimeError(f'Unknown Line: ({line_no}) {line}')

    def split(self, line):
        work = line.split('=')
        if work[0] == "Index":
            # Indexは==となっている。
            # FIXME 恐らくIndex名を指定した場合を考慮する必要あり
            return work[0], work[2]
        return work[0], work[1]

    def parse_entity(self, name, value):
        if name == 'PName':
            self.session.table_name = value
        if name == 'LName':
            self.session.display_name = value
        if name == 'Page':
            value = value.upper()
            self.session.instance = self.mapping[value] if value in self.mapping else None
        if name == "Field":
            self.session.fields.append(value)
        if name == "Index":
            self.session.indexes.append(value)

    def parse_relation(self, name, value):
        if name == "Entity1":
            self.session.entity1 = value
        if name == "Entity2":
            self.session.entity2 = value
        if name == "Fields1":
            self.session.fields1 = value
        if name == "Fields2":
            self.session.fields2 = value

    def parse_comment(self, name, value):
        if name == "Comment":
            self.session.comment = value
        if name == "Page":
            self.session.page = value


def convert_to_schema(p):
    schemas = SchemaManager()

    # Create schemas from instances (tables) and comments
    all_schema_names = set(p.instances.keys())
    # Add schema names from comments that are mapped
    for comment in p.comments:
        if comment.page and comment.page.upper() in p.mapping:
            mapped_schema = p.mapping[comment.page.upper()]
            all_schema_names.add(mapped_schema)

    for k in all_schema_names:
        schema = Schema(name=k)

        # Add standalone comments as schema-level notes
        schema_comments = [
            comment for comment in p.comments
            if comment.page and p.mapping.get(comment.page.upper()) == k
        ]
        for comment in schema_comments:
            if comment.comment:
                # Create note with page as title and comment as content
                note = Note(
                    title=f"Comment from {comment.page}",
                    content=comment.comment.replace('\\n', '\n')  # Convert escaped newlines
                )
                schema.notes.append(note)

        schemas.append(schema)

    # Add standalone comments that don't belong to any specific schema
    for comment in p.comments:
        if comment.page and comment.page.upper() not in p.mapping:
            # Create a 'general' schema if it doesn't exist
            if 'general' not in [s.name for s in schemas.schemas.values()]:
                general_schema = Schema(name='general')
                schemas.append(general_schema)
            else:
                general_schema = next(s for s in schemas.schemas.values() if s.name == 'general')

            if comment.comment:
                note = Note(
                    title=f"Comment from {comment.page}",
                    content=comment.comment.replace('\\n', '\n')
                )
                general_schema.notes.append(note)

    for key, entities in p.instances.items():
        for entity in entities:
            tbl = Table(
                instance=key,
                table_name=entity.table_name,
                display_name=entity.display_name or entity.table_name
            )
            schemas[key].tables.append(tbl)
            relation = p.relations[entity.table_name] if entity.table_name in p.relations else {}
            for row in csv.reader(entity.fields):
                # Convert column type string to ColumnType object
                try:
                    column_type_obj = parse_column_type(row[2])
                except (ValueError, IndexError):
                    # Fallback to simple string if parsing fails
                    from dbgear.models.column_type import ColumnType
                    column_type_obj = ColumnType(column_type=row[2], base_type=row[2])

                # Create notes list if comment exists
                notes = []
                if len(row) > 6 and row[6]:
                    notes.append(Note(title="Import Comment", content=row[6]))

                column = Column(
                    display_name=row[0],
                    column_name=row[1],
                    column_type=column_type_obj,
                    nullable=row[3] != 'NOT NULL',
                    primary_key=int(row[4]) if row[4] != '' else None,
                    default_value=row[5] if row[5] != '' else None,
                    notes=notes
                )
                tbl.columns.append(column)

            for cnt, row in enumerate(csv.reader(entity.indexes)):
                idx = Index(
                    index_name=f'{entity.table_name}_ix{cnt+1}',  # Problem
                    columns=row[1:]
                )
                tbl.indexes.append(idx)

    # Process relations after all tables are created
    for key, entities in p.instances.items():
        for entity in entities:
            tbl = schemas[key].tables[entity.table_name]
            relation_info = p.relations.get(entity.table_name, {})

            for column_name, relation in relation_info.items():
                # Create relation from child table to parent table
                target_entity = EntityInfo(
                    schema_name=key,  # Assuming same schema
                    table_name=relation.entity1
                )

                bind_column = BindColumn(
                    source_column=column_name,
                    target_column=relation.fields1.split(',')[0]  # Take first field if multiple
                )

                rel = Relation(
                    target=target_entity,
                    bind_columns=[bind_column],
                    cardinarity_source='*',  # Many-to-one relationship
                    cardinarity_target='1',
                    constraint_name=f"FK_{entity.table_name}_{relation.entity1}",
                    description=f"Foreign key from {entity.table_name}.{column_name} to {relation.entity1}.{relation.fields1}"
                )

                tbl.relations.append(rel)

    return schemas


def retrieve(folder, filename, mapping, **kwargs):
    """
    Import schema from A5:SQL Mk-2 (.a5er) file.

    Args:
        folder: Directory path containing the file
        filename: Name of the .a5er file to import
        mapping: Schema mapping dictionary (e.g., {'MAIN': 'main'})
        **kwargs: Additional options (unused)

    Returns:
        SchemaManager: The imported schema manager object
    """
    p = Parser(mapping)
    with open(f'{folder}/{filename}', 'r', encoding='utf-8-sig') as f:
        for idx, line in enumerate(f):
            p.parse_line(idx + 1, line.strip())
        # 最後の空行をパースさせる。（ファイル終端で処理されないため）
        p.parse_line(idx+1, '')

    return convert_to_schema(p)

import pydantic
import yaml
import pathlib
import os

from .base import BaseSchema
from .schema import Schema
from .schema import SchemaManager
from .datamodel import DataModel
from .exceptions import DBGearEntityNotFoundError
from .exceptions import DBGearEntityRemovalError
from ..utils.fileio import save_model


class Mapping(BaseSchema):
    folder: str = pydantic.Field(exclude=True)
    environ: str = pydantic.Field(exclude=True)
    name: str = pydantic.Field(exclude=True)
    tenant_name: str | None = pydantic.Field(default=None, exclude=True)
    description: str
    schemas: list[str] = []
    deploy: bool = False

    @classmethod
    def _directory(cls, folder: str, environ: str, name: str) -> str:
        return os.path.join(folder, environ, name)

    @classmethod
    def _fullpath(cls, folder: str, environ: str, name: str) -> str:
        return os.path.join(folder, environ, name, '_mapping.yaml')

    @classmethod
    def load(cls, folder: str, environ: str, name: str):
        with open(Mapping._fullpath(folder, environ, name), 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return cls(
            folder=folder,
            environ=environ,
            name=name,
            **data
        )

    def save(self):
        path = Mapping._directory(self.folder, self.environ, self.name)
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

        with open(Mapping._fullpath(self.folder, self.environ, self.name), 'w', encoding='utf-8') as f:
            save_model(self, f)

    def delete(self):
        path = Mapping._directory(self.folder, self.environ, self.name)
        if not os.path.exists(path):
            raise DBGearEntityNotFoundError(f'Mapping {self.name} does not exist in {self.folder}/{self.environ}')
        files = [f for f in os.listdir(path) if f != '_mapping.yaml']
        if files:
            raise DBGearEntityRemovalError(f'Cannot remove {path}: files other than _mapping.yaml exist')
        os.remove(Mapping._fullpath(self.folder, self.environ, self.name))
        os.rmdir(path)

    def build_schema(self, project_schema: SchemaManager, environ_schema: SchemaManager | None) -> Schema:
        schema = Schema(name=self.name)
        for name in self.schemas:
            if name in project_schema:
                schema.merge(project_schema[name])
            if environ_schema is not None and name in environ_schema:
                schema.merge(environ_schema[name])
        return schema

    @property
    def instance_name(self) -> str:
        return self.tenant_name or self.name

    @property
    def datamodels(self):
        for path in sorted(pathlib.Path(self.folder).glob(f'{self.environ}/{self.name}/*.yaml')):
            if path.name != '_mapping.yaml':
                schema_name, table_name = path.stem.split('@')
                yield DataModel.load(
                    folder=self.folder,
                    environ=self.environ,
                    map_name=self.name,
                    schema_name=schema_name,
                    table_name=table_name,
                    tenant_name=self.tenant_name,
                )

    def datamodel(self, schema_name: str, table_name: str) -> DataModel:
        # 直接指定の場合は、パスが存在するか確認する。
        path = pathlib.Path(self.folder, self.environ, self.name, f'{schema_name}@{table_name}.yaml')
        if not path.exists():
            return None
        return DataModel.load(
            folder=self.folder,
            environ=self.environ,
            map_name=self.name,
            schema_name=schema_name,
            table_name=table_name,
            tenant_name=self.tenant_name,
        )


class MappingManager:

    def __init__(self, folder: str, environ: str):
        self.folder = folder
        self.environ = environ

    def __getitem__(self, key: str) -> Mapping:
        return Mapping.load(self.folder, self.environ, key)

    def __iter__(self):
        for path in sorted(pathlib.Path(self.folder).glob(f'{self.environ}/*/_mapping.yaml')):
            name = str(path.parent.relative_to(pathlib.Path(self.folder) / self.environ))
            yield Mapping.load(self.folder, self.environ, name)

    def __contains__(self, key: str) -> bool:
        return os.path.exists(Mapping._fullpath(self.folder, self.environ, key))

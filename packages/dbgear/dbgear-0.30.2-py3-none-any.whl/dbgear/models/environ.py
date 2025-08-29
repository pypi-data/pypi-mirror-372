import pydantic
import yaml
import pathlib
import os

from .base import BaseSchema
from .schema import SchemaManager
from .mapping import MappingManager
from .tenant import TenantRegistry
from .exceptions import DBGearEntityNotFoundError
from .exceptions import DBGearEntityRemovalError
from ..utils.fileio import save_model


class Environ(BaseSchema):
    folder: str = pydantic.Field(exclude=True)
    name: str = pydantic.Field(exclude=True)
    description: str
    deployments: dict[str, str] = {}

    _schemas: SchemaManager | None = None
    _tenant: TenantRegistry | None = None

    @classmethod
    def _directory(cls, folder, name) -> str:
        return os.path.join(folder, name)

    @classmethod
    def _fullpath(cls, folder, name) -> str:
        return os.path.join(folder, name, 'environ.yaml')

    @classmethod
    def load(cls, folder: str, name: str) -> None:
        with open(cls._fullpath(folder, name), 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return cls(
            folder=folder,
            name=name,
            **data)

    def save(self) -> None:
        path = Environ._directory(self.folder, self.name)
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

        with open(Environ._fullpath(self.folder, self.name), 'w', encoding='utf-8') as f:
            save_model(self, f)

    def delete(self) -> None:
        path = Environ._directory(self.folder, self.name)
        if not os.path.exists(path):
            raise DBGearEntityNotFoundError(f'Environment {self.name} does not exist in {self.folder}')
        files = [f for f in os.listdir(path) if f != 'environ.yaml']
        if files:
            raise DBGearEntityRemovalError(f'Cannot remove {path}: files other than environ.yaml exist')
        os.remove(Environ._fullpath(self.folder, self.name))
        os.rmdir(path)

    @property
    def schemas(self) -> SchemaManager | None:
        if self._schemas is None:
            self._schemas = SchemaManager.load(f'{self.folder}/{self.name}/schema.yaml')
        return self._schemas

    @property
    def tenant(self) -> TenantRegistry | None:
        if self._tenant is None:
            self._tenant = TenantRegistry.load(self.folder, self.name)
        return self._tenant

    @property
    def mappings(self) -> MappingManager:
        return MappingManager(self.folder, self.name)

    @property
    def databases(self):
        for map in self.mappings:
            if map.deploy:
                yield map
        if self.tenant is not None:
            yield from self.tenant.materialize()


class EnvironManager:

    def __init__(self, folder: str):
        self.folder = folder

    def __getitem__(self, key: str) -> Environ:
        return Environ.load(self.folder, key)

    def __iter__(self):
        for path in sorted(pathlib.Path(self.folder).glob('*/environ.yaml')):
            name = str(path.parent.relative_to(self.folder))
            yield Environ.load(self.folder, name)

    def __contains__(self, name: str) -> bool:
        return os.path.exists(Environ._fullpath(self.folder, name))

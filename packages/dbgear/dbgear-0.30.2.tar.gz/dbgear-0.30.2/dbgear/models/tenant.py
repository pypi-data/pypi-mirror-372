import pydantic
import yaml
import os
import importlib

from .base import BaseSchema
from .mapping import Mapping
from .exceptions import DBGearEntityExistsError
from .exceptions import DBGearEntityNotFoundError
from ..utils.populate import auto_populate_from_keys


class DatabaseInfo(BaseSchema):
    database: str
    description: str | None = None
    active: bool = True


class TenantConfig(BaseSchema):
    name: str = pydantic.Field(exclude=True)
    ref: str

    # tenant variables
    databases: str | list[DatabaseInfo]


class TenantRegistry(BaseSchema):
    """Registry of tenant configurations"""
    folder: str = pydantic.Field(exclude=True)
    name: str = pydantic.Field(exclude=True)
    tenants: dict[str, TenantConfig] = pydantic.Field(default_factory=dict)

    @classmethod
    def load(cls, folder: str, name: str):
        path = f'{folder}/{name}/tenant.yaml'
        if not os.path.exists(path):
            return None
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        populated_data = auto_populate_from_keys(data, {
            'tenants.$1.name': '$1',
        })
        return cls(
            folder=folder,
            name=name,
            **populated_data
        )

    def save(self) -> None:
        """Save tenant configurations to a YAML file"""
        with open(f'{self.folder}/{self.name}/tenant.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(
                self.model_dump(
                    by_alias=True,
                    exclude_none=True,
                    exclude_defaults=True
                ),
                f,
                indent=2,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False)

    def __getitem__(self, name: str) -> TenantConfig:
        return self.tenants[name]

    def __iter__(self):
        yield from self.tenants.values()

    def __len__(self) -> int:
        return len(self.tenants)

    def __contains__(self, name: str) -> bool:
        return name in self.tenants

    def append(self, tenant: TenantConfig) -> None:
        if tenant.name in self.tenants:
            raise DBGearEntityExistsError(f'Tenant {tenant.name} already exists')
        self.tenants[tenant.name] = tenant

    def remove(self, name: str) -> None:
        if name not in self.tenants:
            raise DBGearEntityNotFoundError(f'Tenant {name} does not exist')
        del self.tenants[name]

    def materialize(self):
        for tenant in self.tenants.values():
            map = Mapping.load(self.folder, self.name, tenant.ref)

            if type(tenant.databases) is str:
                module = importlib.import_module(tenant.databases)
                method_name = "retrieve"
                method = getattr(module, method_name)
                for tenant_map in method(map):
                    yield tenant_map
            else:
                for database in tenant.databases:
                    if not database.active:
                        continue
                    clone = map.model_copy(deep=True)
                    clone.tenant_name = database.database
                    yield clone

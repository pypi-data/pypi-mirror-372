import pydantic
import yaml
import pathlib
import os

from typing import Any

from .base import BaseSchema
from .datasources.factory import Factory
from ..utils import const
from ..utils.fileio import save_model


class SettingInfo(BaseSchema):
    setting_type: str
    width: int | None = None
    environ: str | None = None
    schema_name: str | None = None
    table_name: str | None = None


class DataParams(BaseSchema):
    layout: str | None = None
    settings: dict[str, SettingInfo] = pydantic.Field(default_factory=dict)
    value: str | None = None
    caption: str | None = None
    segment: str | None = None
    x_axis: str | None = None
    y_axis: str | None = None
    cells: list[str] | None = None


class DataModel(BaseSchema):
    folder: str = pydantic.Field(exclude=True)
    environ: str = pydantic.Field(exclude=True)
    map_name: str = pydantic.Field(exclude=True)
    schema_name: str = pydantic.Field(exclude=True)
    table_name: str = pydantic.Field(exclude=True)
    tenant_name: str | None = pydantic.Field(default=None, exclude=True)
    description: str
    sync_mode: str
    data_type: str
    data_path: str | None = None
    data_args: dict[str, Any] = pydantic.Field(default_factory=dict)
    data_params: DataParams = pydantic.Field(default_factory=DataParams)
    dependencies: list[str] = pydantic.Field(default_factory=list)  # ["schema@table", "other_schema@other_table"]

    @classmethod
    def _directory(cls, folder: str, environ: str, map_name: str) -> str:
        return os.path.join(folder, environ, map_name)

    @classmethod
    def _filename(cls, schema_name: str, table_name: str) -> str:
        return f'{schema_name}@{table_name}.yaml'

    @classmethod
    def _fullpath(cls, folder: str, environ: str, map_name: str, schema_name: str, table_name: str) -> str:
        return os.path.join(folder, environ, map_name, DataModel._filename(schema_name, table_name))

    @classmethod
    def load(cls, folder: str, environ: str, map_name: str, schema_name: str, table_name: str, tenant_name: str | None = None):
        with open(DataModel._fullpath(folder, environ, map_name, schema_name, table_name), 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return cls(
            folder=folder,
            environ=environ,
            map_name=map_name,
            schema_name=schema_name,
            table_name=table_name,
            tenant_name=tenant_name,
            **data
        )

    def save(self) -> None:
        with open(DataModel._fullpath(self.folder, self.environ, self.map_name, self.schema_name, self.table_name), 'w', encoding='utf-8') as f:
            save_model(self, f)

    def delete(self) -> None:
        path = DataModel._fullpath(self.folder, self.environ, self.map_name, self.schema_name, self.table_name)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Data model file {self._filename(self.schema_name, self.table_name)} does not exist.")
        if self.data_type == const.DATATYPE_YAML:
            for ds in self.datasources:
                path = os.path.join(self.folder, self.environ, self.map_name, ds.filename)
                if os.path.exists(path):
                    os.remove(path)
        os.remove(path)

    @property
    def datasources(self):
        if self.data_params.segment is None:
            yield Factory.create(
                data_type=self.data_type,
                folder=self.folder,
                environ=self.environ,
                name=self.map_name,
                schema_name=self.schema_name,
                table_name=self.table_name,
                tenant_name=self.tenant_name,
                data_path=self.data_path,
                **self.data_args,
            )

        for path in sorted(pathlib.Path(self.folder, self.environ, self.map_name).glob(f"{self.schema_name}@{self.table_name}#*.dat")):
            seg = path.stem.split('#', 1)[1] if '#' in path.stem else None
            yield Factory.create(
                data_type=self.data_type,
                folder=self.folder,
                environ=self.environ,
                name=self.map_name,
                schema_name=self.schema_name,
                table_name=self.table_name,
                segment=seg,
                tenant_name=self.tenant_name,
                data_path=self.data_path,
                **self.data_args,
            )

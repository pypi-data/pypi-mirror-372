import importlib

from .base import BaseDataSource
from ...utils import const


class Factory:
    @staticmethod
    def create(data_type: str, data_path: str | None, **kwargs) -> BaseDataSource:
        """
        動的にdata_typeに対応するDataSourceクラスのインスタンスを生成する

        Args:
            data_type (str): データソースの種類（例: 'mysql', 'postgres' など）
            *args, **kwargs: DataSourceクラスのコンストラクタ引数

        Returns:
            DataSource: 指定されたデータソースのインスタンス
        """
        if data_type == const.DATATYPE_PYTHON:
            module = importlib.import_module(data_path)
            class_name = "DataSource"
            data_source_class = getattr(module, class_name)
            return data_source_class(**kwargs)
        else:
            try:
                module_name = f".{data_type}source"
                class_name = "DataSource"
                module = importlib.import_module(module_name, __package__)
                data_source_class = getattr(module, class_name)
                return data_source_class(data_path=data_path, **kwargs)
            except (ModuleNotFoundError, AttributeError) as e:
                raise ValueError(f"DataSource for '{data_type}' not found: {e}")

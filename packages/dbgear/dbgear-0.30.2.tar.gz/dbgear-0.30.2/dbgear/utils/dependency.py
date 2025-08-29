from graphlib import TopologicalSorter, CycleError
from logging import getLogger

logger = getLogger(__name__)


class DependencyResolver:
    """データ投入時の依存関係を解決するためのクラス"""

    def resolve_insertion_order(self, datamodels, schema):
        """
        DataModelリストを依存関係に基づいて並び替える

        Args:
            datamodels: DataModelのイテラブル
            schema: Schema オブジェクト

        Returns:
            list[DataModel]: 依存関係順に並び替えられたDataModelリスト

        Raises:
            CycleError: 循環依存が検出された場合
        """
        # DataModelをリストに変換し、キーマップを作成
        datamodels_list = list(datamodels)
        dependencies = {}
        datamodel_map = {}

        # 各DataModelの依存関係を収集
        for dm in datamodels_list:
            key = f"{dm.schema_name}@{dm.table_name}"
            datamodel_map[key] = dm

            deps = set()

            # 1. FK依存関係を抽出（スキーマから）
            if dm.table_name in schema.tables:
                table = schema.tables[dm.table_name]
                for relation in table.relations:
                    target_key = f"{relation.target.schema_name}@{relation.target.table_name}"
                    
                    # 自己参照リレーションを除外
                    if target_key == key:
                        logger.debug(f"Skipping self-reference: {key} -> {target_key}")
                        continue
                    
                    # 同じデータセット内にある依存関係のみ追加
                    if any(target_dm.schema_name == relation.target.schema_name and
                          target_dm.table_name == relation.target.table_name
                          for target_dm in datamodels_list):
                        deps.add(target_key)
                        logger.debug(f"FK dependency: {key} -> {target_key}")

            # 2. DataModelの明示的依存関係を追加
            for dep in dm.dependencies:
                # 同じデータセット内にある依存関係のみ追加
                if any(f"{target_dm.schema_name}@{target_dm.table_name}" == dep
                      for target_dm in datamodels_list):
                    deps.add(dep)
                    logger.debug(f"Explicit dependency: {key} -> {dep}")

            dependencies[key] = deps

        try:
            # TopologicalSorterで順序解決
            ts = TopologicalSorter(dependencies)
            ordered_keys = list(ts.static_order())

            # DataModelオブジェクトの順序で返す
            result = [datamodel_map[key] for key in ordered_keys if key in datamodel_map]

            logger.info(f"Resolved insertion order: {[f'{dm.schema_name}@{dm.table_name}' for dm in result]}")
            return result

        except CycleError as e:
            logger.error(f"Circular dependency detected in data insertion order: {e}")
            raise ValueError(f"Circular dependency detected: {e}")

    def validate_dependencies(self, datamodels, schema):
        """
        依存関係の妥当性を検証する

        Args:
            datamodels: DataModelのイテラブル
            schema: Schema オブジェクト

        Returns:
            list[str]: 警告メッセージのリスト
        """
        warnings = []
        datamodels_list = list(datamodels)
        available_tables = {f"{dm.schema_name}@{dm.table_name}" for dm in datamodels_list}

        for dm in datamodels_list:
            # 明示的依存関係の存在チェック
            for dep in dm.dependencies:
                if dep not in available_tables:
                    warnings.append(f"Table {dm.schema_name}@{dm.table_name} depends on {dep}, but it's not in the data insertion set")

            # FK依存関係の存在チェック
            if dm.table_name in schema.tables:
                table = schema.tables[dm.table_name]
                for relation in table.relations:
                    target_key = f"{relation.target.schema_name}@{relation.target.table_name}"
                    current_key = f"{dm.schema_name}@{dm.table_name}"
                    
                    # 自己参照リレーションを除外
                    if target_key == current_key:
                        continue
                    
                    if target_key not in available_tables:
                        warnings.append(f"Table {dm.schema_name}@{dm.table_name} has FK to {target_key}, but it's not in the data insertion set")

        return warnings

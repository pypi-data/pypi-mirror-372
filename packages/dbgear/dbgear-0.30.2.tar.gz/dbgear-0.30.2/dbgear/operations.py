from logging import getLogger
from datetime import datetime

from .dbio import engine
from .dbio import database
from .dbio import table
from .dbio import view
from .dbio import trigger
from .dbio import procedure

from .models.project import Project
from .models.mapping import Mapping
from .models.schema import Schema
from .utils import const

logger = getLogger(__name__)


class Operation:

    def __init__(self, project: Project, env: str, database: str, deploy: str):
        self.project = project
        self.environ = project.envs[env]
        self.database = database

        self.conn = engine.get_connection(self.environ.deployments[deploy])
        self.ymd = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def create_database(self, map: Mapping, all: str):
        if all == 'drop':
            logger.info(f'database {map.instance_name}')
            if database.is_exist(self.conn, map.instance_name):
                database.drop(self.conn, map.instance_name)
            database.create(self.conn, map.instance_name)
        else:
            # 差分更新または個別指定の場合で、データベースが存在しない場合は作成する。
            if not database.is_exist(self.conn, map.instance_name):
                logger.info(f'database {map.instance_name} was created.')
                database.create(self.conn, map.instance_name)

    def create_table(self, map: Mapping, schema: Schema, all: str, target: str):
        for tbl in schema.tables:
            if not all and target != tbl.table_name:
                continue
            # テーブルが存在しない場合は作成する。
            if not table.is_exist(self.conn, map.instance_name, tbl):
                logger.info(f'table {map.instance_name}.{tbl.table_name} was created.')
                table.create(self.conn, map.instance_name, tbl)
                continue
            # データのバックアップ
            logger.info(f'backup {map.instance_name}.{tbl.table_name}')
            table.backup(self.conn, map.instance_name, tbl, self.ymd)
            # テーブルの再作成
            logger.info(f'drop & create table {map.instance_name}.{tbl.table_name}')
            table.drop(self.conn, map.instance_name, tbl)
            table.create(self.conn, map.instance_name, tbl)

        for vw in schema.views:
            if not all and target != vw.view_name:
                continue
            # ビューが存在しない場合は作成する。
            if not view.is_exist(self.conn, map.instance_name, vw):
                logger.info(f'view {map.instance_name}.{vw.view_name} was created.')
                view.create(self.conn, map.instance_name, vw)
            else:
                # ビューの再作成
                logger.info(f'drop & create view {map.instance_name}.{vw.view_name}')
                view.drop(self.conn, map.instance_name, vw)
                view.create(self.conn, map.instance_name, vw)

        for tr in schema.triggers:
            if not all and target != tr.trigger_name:
                continue
            # トリガーが存在しない場合は作成する。
            if not trigger.is_exist(self.conn, map.instance_name, tr):
                logger.info(f'trigger {map.instance_name}.{tr.trigger_name} was created.')
                trigger.create(self.conn, map.instance_name, tr)
            else:
                # トリガーの再作成
                logger.info(f'drop & create trigger {map.instance_name}.{tr.trigger_name}')
                trigger.drop(self.conn, map.instance_name, tr)
                trigger.create(self.conn, map.instance_name, tr)

        for proc in schema.procedures:
            if not all and target != proc.procedure_name:
                continue
            # プロシージャが存在しない場合は作成する。
            if not procedure.is_exist(self.conn, map.instance_name, proc):
                logger.info(f'procedure {map.instance_name}.{proc.procedure_name} was created.')
                procedure.create(self.conn, map.instance_name, proc)
            else:
                # プロシージャの再作成
                logger.info(f'drop & create procedure {map.instance_name}.{proc.procedure_name}')
                procedure.drop(self.conn, map.instance_name, proc)
                procedure.create(self.conn, map.instance_name, proc)

    def insert_data(self, map: Mapping, schema: Schema, all: bool, target: str):
        # データ投入の順序を決定
        if all:
            # 全体指定時は依存関係を考慮した順序でデータ投入
            from .utils.dependency import DependencyResolver
            resolver = DependencyResolver()

            # 依存関係の妥当性をチェック
            warnings = resolver.validate_dependencies(map.datamodels, schema)
            for warning in warnings:
                logger.warning(warning)

            try:
                ordered_datamodels = resolver.resolve_insertion_order(map.datamodels, schema)
            except ValueError as e:
                logger.error(f"Failed to resolve data insertion order: {e}")
                raise

            datamodels_to_process = ordered_datamodels
        else:
            # 個別指定時は従来通り
            datamodels_to_process = map.datamodels

        # データ投入処理
        for dm in datamodels_to_process:
            if dm.sync_mode == const.SYNC_MODE_MANUAL and all:
                # 手動モードで全てで指定されている場合には、スキップする
                continue
            # FIXME テーブルレイアウトが変わっている場合は、データの挿入ができない。
            if not all and target != dm.table_name:
                continue
            tbl = schema.tables[dm.table_name]
            for ds in dm.datasources:
                logger.info(f'insert {ds.filename} to {map.instance_name}.{tbl.table_name}')
                ds.load()
                table.insert(self.conn, map.instance_name, tbl, ds.data)

            if dm.sync_mode != const.SYNC_MODE_DROP_CREATE:
                # 同期モードがdrop_create以外の場合は、データのリストアを行う。
                if table.is_exist_backup(self.conn, map.instance_name, tbl, self.ymd):
                    # バックアップからデータを復元(同じIDは更新されるため、初期データの変更分は上書きされる)
                    logger.info(f'restore {map.instance_name}.{tbl.table_name}')
                    table.restore(self.conn, map.instance_name, tbl, self.ymd)

            engine.commit(self.conn)

    # ユニットテストなどで、Operationのインスタンスを取得するためのメソッド
    @staticmethod
    def get_instance(folder: str, env: str, database: str, deploy: str):
        project = Project.load(folder)
        return Operation(project, env, database, deploy)

    def reset_all(self):
        for map in self.environ.databases:
            if self.database is not None and map.instance_name != self.database:
                continue

            self.create_database(map, 'drop')
            schema = map.build_schema(self.project.schemas, self.environ.schemas)
            self.create_table(map, schema, all, None)

    def require(self, database: str, schema_name: str, table_name: str):
        for map in self.environ.databases:
            if self.database is not None and map.instance_name != self.database:
                continue
            if map.name != database:
                continue
            schema = map.build_schema(self.project.schemas, self.environ.schemas)
            tbl = schema.tables[table_name]
            dm = map.datamodel(schema_name, table_name)
            if dm is not None:
                for ds in dm.datasources:
                    logger.info(f'insert {ds.filename} to {map.instance_name}.{tbl.table_name}')
                    ds.load()
                    table.insert(self.conn, map.instance_name, tbl, ds.data)


def apply(project, env: str, database: str, target: str, all: str, deploy: str):
    """ データベースの適用処理を行う。 CLI向け関数. """
    with Operation(project, env, database, deploy) as op:
        for map in op.environ.databases:
            if database is not None and map.instance_name != database:
                continue
            # データベースの作成
            op.create_database(map, all)

            schema = map.build_schema(op.project.schemas, op.environ.schemas)
            op.create_table(map, schema, all, target)
            op.insert_data(map, schema, all, target)

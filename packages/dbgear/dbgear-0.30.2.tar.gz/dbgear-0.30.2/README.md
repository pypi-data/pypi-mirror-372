# DBGear

データベース初期データ管理のためのコアライブラリとCLIツールです。

## インストール

```bash
pip install dbgear
```

## 使用方法

### CLIコマンド

#### スキーマインポート
```bash
# A5:SQL Mk-2ファイルからスキーマをインポート
dbgear import a5sql_mk2 schema.a5er

# 出力ファイルを指定
dbgear import a5sql_mk2 schema.a5er --output my_schema.yaml

# スキーママッピングを指定
dbgear import a5sql_mk2 schema.a5er --mapping "MAIN:production,SUB:development"

# ヘルプ表示
dbgear import --help
```

#### データベース適用
```bash
# データベースへの適用
dbgear apply <deployment> <environment> [options]

# 例：全テーブルを削除して再作成
dbgear apply localhost development --all drop

# 例：差分のみ適用
dbgear apply localhost development --all delta

# 例：特定のテーブルのみ適用
dbgear apply localhost development --target users
```

### プログラムでの利用

#### スキーマインポート
```python
from dbgear.core.importer import import_schema

# A5:SQL Mk-2ファイルからインポート
schema_manager = import_schema('a5sql_mk2', 'path/to', 'schema.a5er', {'MAIN': 'main'})

# YAMLファイルに保存
from dbgear.core.models.fileio import save_model
save_model('schema.yaml', schema_manager)
```

#### プロジェクト管理
```python
from dbgear.core.models.project import Project
from dbgear.core.operations import Operation
from dbgear.core.models.schema import SchemaManager, Table, Column

# プロジェクト読み込み
project = Project("./my-project")
project.read_definitions()

# データベース操作
with Operation(project, "development", "localhost") as op:
    op.reset_all()  # 全テーブルをリセット
    op.require("main", "users")  # 特定のテーブルデータを挿入

# スキーマ管理
manager = SchemaManager("./my-project")
schema = manager.create_schema("main")

# テーブル追加（表現式対応）
table = Table(
    table_name="users",
    display_name="ユーザー"
)

# カラムを追加
table.add_column(Column(
    column_name="id",
    display_name="ID",
    column_type="BIGINT",
    nullable=False,
    primary_key=1,
    auto_increment=True
))

table.add_column(Column(
    column_name="name",
    display_name="名前",
    column_type="VARCHAR(100)",
    nullable=False,
    charset="utf8mb4",
    collation="utf8mb4_unicode_ci"
))

table.add_column(Column(
    column_name="full_name",
    display_name="フルネーム",
    column_type="VARCHAR(201)",
    nullable=False,
    expression="CONCAT(first_name, ' ', last_name)",
    stored=True
))

schema.add_table(table)
manager.save()  # YAML保存
```

## 機能

### スキーマインポート
- **A5:SQL Mk-2インポート**: .a5erファイルからDBGear形式への変換
- **動的インポーター**: importlibによる拡張可能なアーキテクチャ
- **スキーママッピング**: 外部形式からDBGearスキーマ名への柔軟なマッピング
- **CLIサポート**: `dbgear import`コマンドによる簡単な変換

### データベーススキーマ管理
- **多形式対応**: A5:SQL Mk-2、MySQL直接接続、独自YAML形式対応
- **スキーマ操作**: テーブル・カラム・インデックス・ビューの追加・更新・削除
- **カラム式サポート**: MySQL生成カラム（GENERATED ALWAYS AS）対応
- **拡張カラム属性**: AUTO_INCREMENT、文字セット、照合順序指定
- **ビュー管理**: データベースビューの定義と依存関係管理
- **SQLテンプレートエンジン**: Jinja2ベースの統一されたSQL生成システム

### データ管理
- **初期データ管理**: YAML形式でのデータ定義
- **環境管理**: 開発・テスト・本番環境の分離
- **データバインディング**: 自動的な値設定（UUID、現在時刻等）
- **プラグイン機構**: カスタムデータ変換の拡張
- **外部キー整合性**: 参照制約の自動検証

## プロジェクト構成

### project.yaml
```yaml
project_name: MyProject
description: Database initial data management

definitions:
  - type: a5sql_mk2
    filename: ./schema.a5er
    mapping:
      MAIN: main
  # または独自YAML形式を使用
  - type: dbgear_schema
    filename: ./schema.yaml
    mapping:
      main: production

bindings:
  created_at:
    type: fixed
    value: NOW()

deployments:
  localhost: mysql+pymysql://root:password@localhost/mydb
```

### 環境設定
```yaml
# development/_mapping.yaml
id: mydb_dev
instances:
  - main
```

### 独自YAML形式のスキーマ定義

```yaml
# schema.yaml
schemas:
  main:
    tables:
      users:
        display_name: ユーザー
        columns:
          # 主キー（AUTO_INCREMENT）
          - column_name: id
            display_name: ID
            column_type: BIGINT
            nullable: false
            primary_key: 1
            auto_increment: true
            
          # 文字セット指定
          - column_name: first_name
            display_name: 名
            column_type: VARCHAR(50)
            nullable: false
            charset: utf8mb4
            collation: utf8mb4_unicode_ci
            
          - column_name: last_name
            display_name: 姓
            column_type: VARCHAR(50)
            nullable: false
            charset: utf8mb4
            collation: utf8mb4_unicode_ci
            
          - column_name: email
            display_name: メールアドレス
            column_type: VARCHAR(255)
            nullable: false
            foreign_key: contacts.email
            
          # 生成カラム（STORED）
          - column_name: full_name
            display_name: フルネーム
            column_type: VARCHAR(101)
            nullable: false
            expression: "CONCAT(last_name, ' ', first_name)"
            stored: true
            
          # 生成カラム（VIRTUAL）
          - column_name: email_domain
            display_name: メールドメイン
            column_type: VARCHAR(255)
            nullable: true
            expression: "SUBSTRING_INDEX(email, '@', -1)"
            stored: false
            
          # 複雑な式（CASE文）
          - column_name: user_type
            display_name: ユーザー種別
            column_type: VARCHAR(20)
            nullable: false
            expression: "CASE WHEN email LIKE '%@company.com' THEN '社員' ELSE '一般' END"
            stored: true
            
          # タイムスタンプ
          - column_name: created_at
            display_name: 作成日時
            column_type: TIMESTAMP
            nullable: false
            default_value: "CURRENT_TIMESTAMP"
            
        indexes:
          - index_name: idx_email
            columns: [email]
          - index_name: idx_full_name
            columns: [full_name]
```

## ライブラリ構成

- `dbgear.core.models`: データモデルとプロジェクト管理
  - `schema`: Column/Table/View/Schemaクラス（表現式属性対応）
  - `project`: プロジェクト設定管理
  - `fileio`: YAML形式でのスキーマ読み書き
- `dbgear.core.dbio`: データベースI/O操作
  - `templates`: Jinja2ベースSQLテンプレートエンジン（18テンプレート）
- `dbgear.core.importer`: スキーマインポート機能
  - 動的インポーターローダー（importlibベース）
- `dbgear.core.importers`: インポーターモジュール
  - `a5sql_mk2`: A5:SQL Mk-2形式インポーター
- `dbgear.core.operations`: データベース操作オーケストレーション
- `dbgear.cli`: CLIインターフェース

## 表現式機能

### サポートする拡張カラム属性

- **expression**: 生成カラムの式（MySQL GENERATED ALWAYS AS）
- **stored**: STORED（true）またはVIRTUAL（false）の指定
- **auto_increment**: AUTO_INCREMENT属性
- **charset**: 文字セット（VARCHAR等の文字列型で使用）
- **collation**: 照合順序（文字列型で使用）

### 使用例

```python
# 生成カラムの定義
calculated_field = Column(
    column_name="total_price",
    column_type="DECIMAL(10,2)",
    expression="price * (1 + tax_rate)",
    stored=True  # STORED列として保存
)

# AUTO_INCREMENT主キー
id_field = Column(
    column_name="id",
    column_type="BIGINT",
    primary_key=1,
    auto_increment=True
)

# 文字セット指定
name_field = Column(
    column_name="name",
    column_type="VARCHAR(100)",
    charset="utf8mb4",
    collation="utf8mb4_unicode_ci"
)
```

### 制約・検証ルール

- 表現式カラムは `default_value`, `primary_key`, `foreign_key` と併用不可
- AUTO_INCREMENTは主キー必須、nullable不可
- 外部キー参照の整合性チェック
- フィールド名・テーブル名の重複チェック

## Web UIが必要な場合

Web UIでのデータ編集が必要な場合は、`dbgear-web`パッケージをインストールしてください：

```bash
pip install dbgear-web
dbgear-web --project ./my-project --port 5000
```

## 開発

### テスト実行
```bash
task test           # 全テスト実行
task test-fast      # 軽量テストのみ
task lint           # flake8によるコードチェック
task clean          # ビルド成果物のクリーンアップ
```

### 依存関係
```bash
poetry install      # 依存関係のインストール
poetry add package  # パッケージの追加
```

## ライセンス

MIT

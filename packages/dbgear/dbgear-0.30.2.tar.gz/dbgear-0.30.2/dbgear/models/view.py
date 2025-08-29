import pydantic

from .base import BaseSchema
from .notes import Note
from .notes import NoteManager


class ViewColumn:
    column_name: str
    display_name: str
    column_type: str
    nullable: bool
    source_table: str | None = None  # 参照元テーブル
    source_column: str | None = None  # 参照元カラム
    is_computed: bool = False  # 計算列かどうか


class View(BaseSchema):
    """Database view definition"""
    view_name: str = pydantic.Field(exclude=True)
    display_name: str
    select_statement: str
    notes_: list[Note] = pydantic.Field(default_factory=list, alias='notes')

    # 以下は将来のSQL解析で自動生成される予定
    _parsed_columns: list[ViewColumn] = []  # SQL解析結果をキャッシュ
    _dependencies: list[str] = []  # 参照テーブル/ビューを自動検出
    _is_parsed: bool = False  # 解析済みフラグ

    @property
    def notes(self) -> NoteManager:
        return NoteManager(self.notes_)


class ViewManager:

    def __init__(self, views: dict[str, View]):
        self.views = views

    def __getitem__(self, view_name: str) -> View:
        return self.views[view_name]

    def __iter__(self):
        yield from self.views.values()

    def __len__(self) -> int:
        return len(self.views)

    def __contains__(self, view_name: str) -> bool:
        return view_name in self.views

    def append(self, view: View) -> None:
        if view.view_name in self.views:
            raise ValueError(f"View '{view.view_name}' already exists")
        self.views[view.view_name] = view

    def remove(self, view_name: str) -> None:
        if view_name not in self.views:
            raise KeyError(f"View '{view_name}' does not exist")
        del self.views[view_name]

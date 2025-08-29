import pydantic

from .base import BaseSchema
from .notes import Note
from .notes import NoteManager


class Trigger(BaseSchema):
    """Database trigger definition"""
    trigger_name: str = pydantic.Field(exclude=True)
    display_name: str
    table_name: str  # 対象テーブル名
    timing: str  # BEFORE | AFTER | INSTEAD OF
    event: str  # INSERT | UPDATE | DELETE
    condition: str | None = None  # WHEN条件（オプション）
    body: str  # トリガーの実行内容
    notes_: list[Note] = pydantic.Field(default_factory=list, alias='notes')

    @property
    def notes(self) -> NoteManager:
        return NoteManager(self.notes_)


class TriggerManager:

    def __init__(self, triggers: dict[str, Trigger]):
        self.triggers = triggers

    def __getitem__(self, trigger_name: str) -> Trigger:
        return self.triggers[trigger_name]

    def __iter__(self):
        yield from self.triggers.values()

    def __len__(self) -> int:
        return len(self.triggers)

    def __contains__(self, trigger_name: str) -> bool:
        return trigger_name in self.triggers

    def append(self, trigger: Trigger) -> None:
        if trigger.trigger_name in self.triggers:
            raise ValueError(f"Trigger '{trigger.trigger_name}' already exists")
        self.triggers[trigger.trigger_name] = trigger

    def remove(self, trigger_name: str) -> None:
        if trigger_name not in self.triggers:
            raise KeyError(f"Trigger '{trigger_name}' does not exist")
        del self.triggers[trigger_name]

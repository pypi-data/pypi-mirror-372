from .base import BaseSchema


class Note(BaseSchema):
    title: str
    content: str
    checked: bool = False


class NoteManager:

    def __init__(self, notes: list[Note]):
        self.notes = notes

    def __getitem__(self, index: int) -> Note:
        return self.notes[index]

    def __iter__(self):
        yield from self.notes

    def __len__(self) -> int:
        return len(self.notes)

    def append(self, note: Note) -> None:
        self.notes.append(note)

    def remove(self, index: int) -> None:
        note = self.notes[index]
        self.notes.remove(note)

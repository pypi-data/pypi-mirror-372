import pydantic

from .base import BaseSchema
from .notes import Note
from .notes import NoteManager


class ProcedureParameter(BaseSchema):
    """Stored procedure parameter definition"""
    parameter_name: str
    parameter_type: str  # IN | OUT | INOUT
    data_type: str  # VARCHAR(255), INT, etc.
    default_value: str | None = None


class Procedure(BaseSchema):
    """Stored procedure definition"""
    procedure_name: str = pydantic.Field(exclude=True)
    display_name: str
    parameters: list[ProcedureParameter] = pydantic.Field(default_factory=list)
    return_type: str | None = None  # For functions (NULL for procedures)
    body: str  # SQL procedure body
    language: str = "SQL"  # SQL, PLPGSQL for future database support
    deterministic: bool = False
    reads_sql_data: bool = True
    modifies_sql_data: bool = False
    security_type: str = "DEFINER"  # DEFINER | INVOKER
    notes_: list[Note] = pydantic.Field(default_factory=list, alias='notes')

    @property
    def notes(self) -> NoteManager:
        return NoteManager(self.notes_)

    @property
    def is_function(self) -> bool:
        """Returns True if this is a function (has return type), False if procedure"""
        return self.return_type is not None


class ProcedureManager:
    """Manager for stored procedure collections"""

    def __init__(self, procedures: dict[str, Procedure]):
        self.procedures = procedures

    def __getitem__(self, procedure_name: str) -> Procedure:
        return self.procedures[procedure_name]

    def __iter__(self):
        yield from self.procedures.values()

    def __len__(self) -> int:
        return len(self.procedures)

    def __contains__(self, procedure_name: str) -> bool:
        return procedure_name in self.procedures

    def append(self, procedure: Procedure) -> None:
        if procedure.procedure_name in self.procedures:
            raise ValueError(f"Procedure '{procedure.procedure_name}' already exists")
        self.procedures[procedure.procedure_name] = procedure

    def remove(self, procedure_name: str) -> None:
        if procedure_name not in self.procedures:
            raise KeyError(f"Procedure '{procedure_name}' does not exist")
        del self.procedures[procedure_name]

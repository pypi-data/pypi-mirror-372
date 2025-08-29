from .base import BaseSchema


class Options(BaseSchema):
    # Database construction options
    create_foreign_key_constraints: bool = True

    # Future options can be added here
    # create_indexes: bool = True
    # validate_data_integrity: bool = True
    # enable_triggers: bool = True

import yaml
from ..models.base import BaseSchema


def save_model(model: BaseSchema, stream):
    yaml.dump(
        model.model_dump(
            by_alias=True,
            exclude_none=True,
            exclude_defaults=True
        ),
        stream,
        indent=2,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False
    )

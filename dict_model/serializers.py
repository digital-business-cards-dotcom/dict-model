import typing
from datetime import datetime

if typing.TYPE_CHECKING:
    from . import DictModel


def datetime(value: datetime) -> str:
    return value.isoformat()


def dict_model(value: "DictModel") -> dict:
    if value.id is None:
        raise value.NotPersisted(str(value))
    return {"dict_model_name": value.__class__.__name__, "id": value.id}

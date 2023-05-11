import typing

if typing.TYPE_CHECKING:
    from . import DictModel

DICT_MODEL_CLASSES = {}


def dict_model(value: "DictModel") -> dict:
    if value.id is None:
        raise value.NotPersisted(str(value))
    return {"dict_model_name": value.__class__.__name__, "id": value.id}

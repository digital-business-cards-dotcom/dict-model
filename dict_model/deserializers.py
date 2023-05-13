import typing

from .serializers import DICT_MODEL_CLASSES

if typing.TYPE_CHECKING:
    from . import DictModel


def dict_model(value: typing.Any) -> "DictModel":
    dict_model_cls = DICT_MODEL_CLASSES[value["dict_model_name"]]
    return dict_model_cls.objects.get(id=value["id"])

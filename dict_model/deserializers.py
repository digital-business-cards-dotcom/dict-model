import typing

from .lookup import get_dict_model_class

if typing.TYPE_CHECKING:
    from . import DictModel


def dict_model(value: typing.Any) -> "DictModel":
    dict_model_cls = get_dict_model_class(value["dict_model_name"])
    return dict_model_cls.objects.get(id=value["id"])

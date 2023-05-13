import typing

DICT_MODEL_CLASSES = {}


class DictModelNotFound(Exception):
    pass


if typing.TYPE_CHECKING:
    from . import DictModel


def get_dict_model_class(name: str) -> typing.Type["DictModel"]:
    try:
        return DICT_MODEL_CLASSES[name]
    except KeyError:
        raise DictModelNotFound(name)


def set_dict_model_class(name: str, dict_model_class: typing.Type["DictModel"]) -> None:
    DICT_MODEL_CLASSES[name] = dict_model_class

import pytest

from dict_model import lookup

CLASS = "CLASS"


def test_get_dict_model_class_returns_class_for_name():
    lookup.DICT_MODEL_CLASSES["ModelName"] = CLASS
    assert lookup.get_dict_model_class("ModelName") == CLASS


def test_get_dict_model_class_raises_error_if_class_name_not_found():
    with pytest.raises(lookup.DictModelNotFound):
        lookup.get_dict_model_class("ModelName")


def test_set_dict_model_class_sets_name_to_class():
    lookup.set_dict_model_class("ModelName", CLASS)
    assert lookup.DICT_MODEL_CLASSES == {"ModelName": CLASS}

from dataclasses import dataclass

import pytest

import dict_model
from dict_model.query_sets import DictModelQuerySet


def test_dict_model_object_manager_create_saves_object():
    @dataclass
    class Empty(dict_model.DictModel):
        name: str

    object_manager = dict_model.DictModelObjectManager(Empty)
    obj = object_manager.create(name="hello")
    assert obj.name == "hello"
    assert Empty.object_lookup == {1: obj}


def test_dict_model_object_manager_all_returns_query_set_of_all_objects_ordered_by_id():
    @dataclass
    class Soda(dict_model.DictModel):
        name: str

        object_data = {2: {"name": "Coca-Cola"}, 1: {"name": "Pepsi"}}

    Soda.init()

    object_manager = dict_model.DictModelObjectManager(Soda)
    assert object_manager.all() == DictModelQuerySet(
        [Soda(id=1, name="Pepsi"), Soda(id=2, name="Coca-Cola")]
    )


@pytest.mark.parametrize(
    "method, kwargs, return_type",
    [
        ("exclude", {"name": "Spoon"}, DictModelQuerySet),
        ("first", {}, dict_model.DictModel),
        ("filter", {"name": "Fork"}, DictModelQuerySet),
        ("get", {"id": 2}, dict_model.DictModel),
        ("last", {}, dict_model.DictModel),
    ],
)
def test_dict_model_object_manager_delegates_query_set_methods_to_query_set(
    method, kwargs, return_type
):
    @dataclass
    class Silverware(dict_model.DictModel):
        name: str

        object_data = {1: {"name": "Fork"}, 2: {"name": "Spoon"}}

    Silverware.init()
    object_manager = dict_model.DictModelObjectManager(Silverware)
    query_set_method = getattr(object_manager, method)
    assert isinstance(query_set_method(**kwargs), return_type)

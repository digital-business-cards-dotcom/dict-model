from dataclasses import dataclass

import pytest

from dict_models import DictModel
from dict_models.query_sets import DictModelQuerySet


def test_dict_model_query_set_assigns_dict_model_class_explicitly_if_assigned():
    @dataclass
    class Ghost(DictModel):
        age: int

    query_set = DictModelQuerySet(dict_model_class=Ghost)
    assert query_set._dict_model_class == Ghost


def test_dict_model_query_set_assigns_dict_model_class_from_first_item_if_available():
    @dataclass
    class Dog(DictModel):
        name: str

    query_set = DictModelQuerySet([Dog(name="Francis")])
    assert query_set._dict_model_class == Dog


def test_dict_model_query_set_raises_error_if_no_dict_model_class_is_available():
    with pytest.raises(DictModelQuerySet.NoDictModelProvided):
        DictModelQuerySet([])


def test_dict_model_query_set_create_retains_object_lookup():
    @dataclass
    class Cereal(DictModel):
        name: str

    cheerios = Cereal(id=1, name="Cheerios")
    Cereal._object_lookup = {1: cheerios}
    query_set = DictModelQuerySet([], dict_model_class=Cereal)

    chex = query_set.create(name="Chex")
    assert chex.id == 2
    assert chex.name == "Chex"

    assert Cereal._object_lookup == {1: cheerios, 2: chex}


def test_dict_model_query_set_first_returns_first_result_of_query_set():
    @dataclass
    class ToDo(DictModel):
        item: str

    query_set = DictModelQuerySet(
        [
            ToDo(id=1, item="Water plants"),
            ToDo(id=2, item="Eat lunch"),
            ToDo(id=3, item="Go to sleep"),
        ]
    )
    assert query_set.first() == ToDo(id=1, item="Water plants")


def test_dict_model_query_set_first_returns_none_if_query_set_is_empty():
    @dataclass
    class Placeholder(DictModel):
        pass

    query_set = DictModelQuerySet([], dict_model_class=Placeholder)
    assert query_set.first() is None


def test_dict_model_query_set_filter_returns_single_matching_object():
    @dataclass
    class Hello(DictModel):
        name: str

    query_set = DictModelQuerySet([Hello(id=1, name="world"), Hello(id=2, name="foo")])
    assert query_set.filter(id=2) == DictModelQuerySet([Hello(id=2, name="foo")])


def test_dict_model_query_set_filter_returns_multiple_matching_objects():
    @dataclass
    class Vehicle(DictModel):
        name: str
        motorized: bool

    query_set = DictModelQuerySet(
        [
            Vehicle(id=1, name="Car", motorized=True),
            Vehicle(id=2, name="Bicycle", motorized=False),
            Vehicle(id=3, name="Canoe", motorized=False),
            Vehicle(id=4, name="Motorcyle", motorized=True),
        ]
    )
    assert query_set.filter(motorized=False) == DictModelQuerySet(
        [
            Vehicle(id=2, name="Bicycle", motorized=False),
            Vehicle(id=3, name="Canoe", motorized=False),
        ]
    )


def test_dict_model_query_set_filter_returns_empty_set_if_no_results_found():
    @dataclass
    class Foo(DictModel):
        is_bar: bool

    query_set = DictModelQuerySet([Foo(id=1, is_bar=False), Foo(id=2, is_bar=False)])
    assert query_set.filter(is_bar=True) == DictModelQuerySet([], dict_model_class=Foo)


def test_dict_model_query_set_get_returns_single_matching_result():
    @dataclass
    class Letter(DictModel):
        name: str

    query_set = DictModelQuerySet(
        [Letter(id=1, name="A"), Letter(id=2, name="B"), Letter(id=3, name="C")]
    )
    assert query_set.get(name="B") == Letter(id=2, name="B")


def test_dict_model_query_set_get_raises_error_if_no_results_found():
    @dataclass
    class Number(DictModel):
        value: int

    query_set = DictModelQuerySet(
        [Number(id=1, value=42), Number(id=2, value=108), Number(id=3, value=666)]
    )
    with pytest.raises(query_set.DoesNotExist):
        query_set.get(value="B")


def test_dict_model_query_set_get_raises_error_if_multiple_results_found():
    @dataclass
    class Cake(DictModel):
        chocolate: bool

    query_set = DictModelQuerySet(
        [
            Cake(id=1, chocolate=True),
            Cake(id=2, chocolate=False),
            Cake(id=3, chocolate=True),
        ]
    )
    with pytest.raises(query_set.MultipleResultsFound):
        query_set.get(chocolate=True)


def test_dict_model_query_set_last_returns_last_result_of_query_set():
    @dataclass
    class Movie(DictModel):
        name: str

    query_set = DictModelQuerySet(
        [
            Movie(id=1, name="Hereditary"),
            Movie(id=2, name="Point Break"),
            Movie(id=3, name="Emily the Criminal"),
        ]
    )
    assert query_set.last() == Movie(id=3, name="Emily the Criminal")


def test_dict_model_query_set_last_returns_none_if_query_set_is_empty():
    @dataclass
    class Placeholder(DictModel):
        pass

    query_set = DictModelQuerySet([], dict_model_class=Placeholder)
    assert query_set.last() is None

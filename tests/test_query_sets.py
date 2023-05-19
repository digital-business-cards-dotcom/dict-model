from dataclasses import dataclass

import pytest

from dict_model import DictModel
from dict_model.query_sets import DictModelQuerySet


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


def test_dict_model_query_set_all_returns_all_entries():
    @dataclass
    class Message(DictModel):
        value: str

    query_set = DictModelQuerySet([Message(value="hello"), Message(value="welcome")])
    assert query_set.all() == DictModelQuerySet(
        [Message(value="hello"), Message(value="welcome")]
    )


def test_dict_model_query_set_passes_filters_when_attributes_are_equal():
    @dataclass
    class Phone(DictModel):
        name: str

    assert DictModelQuerySet._passes_filters(Phone(name="cell"), name="cell") is True


def test_dict_model_query_set_passes_filters_when_attributes_are_not_equal():
    @dataclass
    class Shoe(DictModel):
        name: str

    assert DictModelQuerySet._passes_filters(Shoe(name="tennis"), name="dress") is False


def test_dict_model_query_set_passes_filters_when_attribute_is_in_set():
    @dataclass
    class Sport(DictModel):
        name: str

    assert (
        DictModelQuerySet._passes_filters(
            Sport(name="surfing"), name__in=["basketball", "surfing"]
        )
        is True
    )


def test_dict_model_query_set_passes_filters_when_attribute_is_not_in_set():
    @dataclass
    class Pillow(DictModel):
        name: str

    assert (
        DictModelQuerySet._passes_filters(
            Pillow(name="throw"), name__in=["regular", "body"]
        )
        is False
    )


def test_dict_model_query_set_exclude_returns_single_matching_object():
    @dataclass
    class Greeting(DictModel):
        text: str
        is_formal: bool

    query_set = DictModelQuerySet(
        [
            Greeting(id=1, text="hello", is_formal=False),
            Greeting(id=2, text="hello, sir", is_formal=True),
        ]
    )

    assert query_set.exclude(is_formal=True) == DictModelQuerySet(
        [Greeting(id=1, text="hello", is_formal=False)]
    )


def test_dict_model_query_set_exclude_returns_multiple_matching_objects():
    @dataclass
    class FastFurious(DictModel):
        number: int
        vin_stars: bool

    query_set = DictModelQuerySet(
        [
            FastFurious(id=1, number=1, vin_stars=True),
            FastFurious(id=2, number=2, vin_stars=False),
            FastFurious(id=3, number=3, vin_stars=False),
            FastFurious(id=4, number=4, vin_stars=True),
        ]
    )

    assert query_set.exclude(vin_stars=False) == DictModelQuerySet(
        [
            FastFurious(id=1, number=1, vin_stars=True),
            FastFurious(id=4, number=4, vin_stars=True),
        ]
    )


def test_dict_model_query_set_exclude_returns_empty_set_if_no_results_found():
    @dataclass
    class TwilightBook(DictModel):
        number: int
        has_mermaids: bool

    query_set = DictModelQuerySet(
        [
            TwilightBook(id=1, number=1, has_mermaids=False),
            TwilightBook(id=2, number=2, has_mermaids=False),
        ]
    )

    assert query_set.exclude(has_mermaids=False) == DictModelQuerySet(
        [], dict_model_class=TwilightBook
    )


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


def test_dict_model_query_set_chaining_multiple_calls():
    @dataclass
    class Truths(DictModel):
        a: bool
        b: bool
        c: bool

    query_set = DictModelQuerySet(
        [
            Truths(id=1, a=True, b=True, c=True),
            Truths(id=2, a=True, b=True, c=False),
            Truths(id=3, a=False, b=True, c=True),
            Truths(id=4, a=False, b=True, c=False),
            Truths(id=5, a=False, b=False, c=True),
        ]
    )

    assert query_set.exclude(a=True).filter(c=True) == DictModelQuerySet(
        [Truths(id=3, a=False, b=True, c=True), Truths(id=5, a=False, b=False, c=True)]
    )


def test_query_set_order_by_sorts_results():
    @dataclass
    class Temperature(DictModel):
        value: int

    query_set = DictModelQuerySet(
        [
            Temperature(id=1, value=100),
            Temperature(id=2, value=50),
            Temperature(id=3, value=75),
            Temperature(id=4, value=25),
        ]
    )
    assert query_set.order_by("value") == DictModelQuerySet(
        [
            Temperature(id=4, value=25),
            Temperature(id=2, value=50),
            Temperature(id=3, value=75),
            Temperature(id=1, value=100),
        ]
    )


def test_query_set_order_by_descending_order():
    @dataclass
    class Number(DictModel):
        value: int

    query_set = DictModelQuerySet(
        [
            Number(id=1, value=100),
            Number(id=2, value=50),
            Number(id=3, value=75),
            Number(id=4, value=25),
        ]
    )
    assert query_set.order_by("-value") == DictModelQuerySet(
        [
            Number(id=1, value=100),
            Number(id=3, value=75),
            Number(id=2, value=50),
            Number(id=4, value=25),
        ]
    )

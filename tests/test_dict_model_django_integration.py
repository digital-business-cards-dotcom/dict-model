from dataclasses import dataclass

from dict_model import DictModel
from dict_model.django import DictModelField

UNSET = "UNSET"


def test_dict_model_field_get_choices_for_dict_model_class_returns_id_and_name_pairs():
    @dataclass
    class Phony(DictModel):
        name: str

        object_data = {
            2: {"name": "Guchi"},
            3: {"name": "Gwuess"},
            1: {"name": "Doclie"},
        }

    Phony.init()

    assert DictModelField.get_choices_for_dict_model_class(Phony) == [
        (1, "Doclie"),
        (2, "Guchi"),
        (3, "Gwuess"),
    ]


def test_dict_model_field_from_db_value_returns_dict_model_object_based_on_id():
    @dataclass
    class ShirtSize(DictModel):
        name: str

        object_data = {1: {"name": "S"}, 2: {"name": "M"}, 3: {"name": "L"}}

    ShirtSize.init()

    field = DictModelField(ShirtSize)
    assert field.from_db_value(2) == ShirtSize(id=2, name="M")


def test_dict_model_field_from_db_value_returns_none_if_provided():
    @dataclass
    class Empty(DictModel):
        pass

    Empty.init()

    field = DictModelField(Empty)
    assert field.from_db_value(None) is None


def test_dict_model_field_from_db_value_coerces_value_into_int_for_id_lookup():
    @dataclass
    class Street(DictModel):
        name: str

        object_data = {1: {"name": "Speedway Blvd"}, 2: {"name": "Stone Ave"}}

    Street.init()

    field = DictModelField(Street)
    assert field.from_db_value("2") == Street(id=2, name="Stone Ave")


def test_dict_model_field_get_prep_value_returns_object_id():
    @dataclass
    class Letters(DictModel):
        name: str

        object_data = {1: {"name": "A"}, 2: {"name": "B"}}

    Letters.init()

    field = DictModelField(Letters)
    assert field.get_prep_value(Letters(id=1, name="A"))


def test_dict_model_field_to_python_returns_value_if_it_is_a_dict_model():
    @dataclass
    class City(DictModel):
        name: str

        object_data = {1: {"name": "Tucson"}}

    City.init()

    field = DictModelField(City)
    assert field.to_python(City(id=1, name="Tucson")) == City(id=1, name="Tucson")


def test_dict_model_field_to_python_returns_none_when_provided():
    @dataclass
    class Void(DictModel):
        pass

    Void.init()

    field = DictModelField(Void)
    assert field.to_python(None) is None


def test_dict_model_field_to_python_looks_up_dict_model_object_from_id():
    @dataclass
    class Fruit(DictModel):
        name: str

        object_data = {1: {"name": "Apple"}, 2: {"name": "Banana"}}

    Fruit.init()

    field = DictModelField(Fruit)
    assert field.to_python(2) == Fruit(id=2, name="Banana")


def test_dict_model_field_to_python_coerces_id_to_int_for_lookup():
    @dataclass
    class Creature(DictModel):
        name: str

        object_data = {1: {"name": "Turtle"}, 2: {"name": "Unicorn"}}

    Creature.init()

    field = DictModelField(Creature)
    assert field.to_python("1") == Creature(id=1, name="Turtle")

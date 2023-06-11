import json
from dataclasses import dataclass
from typing import Optional

import pytest

import dict_model
from dict_model.lookup import DictModelNotFound

from . import TEST_FILES


@pytest.fixture
def example_model():
    @dataclass
    class Example(dict_model.DictModel):
        foo: str
        active: bool = True
        related: Optional[dict_model.DictModel] = None

        def report(self):
            return "None implemented"

        def standard(self):
            return "This is standardized."

    return Example.init()


def test_dict_model_init_with_class_attribute_of_object_data_as_dict_initializes_data():
    @dataclass
    class OtherExample(dict_model.DictModel):
        name: str

        object_data = {1: {"name": "alex"}, 2: {"name": "zoey"}}

    OtherExample.init()

    # Sets object data.
    assert OtherExample.object_lookup == {
        1: OtherExample(id=1, name="alex"),
        2: OtherExample(id=2, name="zoey"),
    }

    # Sets convenience lookup constants.
    assert OtherExample.ALEX == OtherExample(id=1, name="alex")
    assert OtherExample.ZOEY == OtherExample(id=2, name="zoey")


def test_dict_model_init_with_class_attribute_of_object_data_as_list():
    @dataclass
    class AnotherExample(dict_model.DictModel):
        name: str

        object_data = [{"name": "alex"}, {"name": "zoey"}]

    AnotherExample.init()
    assert AnotherExample.object_lookup == {
        1: AnotherExample(id=1, name="alex"),
        2: AnotherExample(id=2, name="zoey"),
    }


def test_dict_model_init_with_object_data_passed_in():
    @dataclass
    class Party(dict_model.DictModel):
        name: str

    Party.init(object_data={1: {"name": "birthday"}, 2: {"name": "office"}})
    assert Party.object_lookup == {
        1: Party(id=1, name="birthday"),
        2: Party(id=2, name="office"),
    }


def test_dict_model_init_with_mix_of_class_attribute_and_passed_in_dict():
    @dataclass
    class Crime(dict_model.DictModel):
        name: str
        severity: int

        object_data = {1: {"name": "Jaywalking", "severity": 1}}

    Crime.init(object_data={2: {"name": "Speeding", "severity": 10}})

    assert Crime.object_lookup == {
        1: Crime(id=1, name="Jaywalking", severity=1),
        2: Crime(id=2, name="Speeding", severity=10),
    }


def test_dict_model_init_with_mix_of_class_attribute_and_passed_in_list():
    @dataclass
    class GoodDeed(dict_model.DictModel):
        name: str
        severity: int

        object_data = [{"name": "Compliment", "severity": 10}]

    GoodDeed.init(object_data=[{"name": "Give money", "severity": 100}])

    assert GoodDeed.object_lookup == {
        1: GoodDeed(id=1, name="Compliment", severity=10),
        2: GoodDeed(id=2, name="Give money", severity=100),
    }


def test_dict_model_init_with_no_preset_object_data():
    @dataclass
    class BusLine(dict_model.DictModel):
        name: str
        frequency: int

    BusLine.init()
    assert BusLine.object_lookup == {}


@pytest.mark.parametrize(
    "cls_object_data,object_data",
    [
        ({1: {"letter": "A"}}, [{"letter": "B"}]),
        ([{"letter": "A"}], {2: {"letter": "B"}}),
    ],
)
def test_dict_model_init_raises_error_with_object_data_type_mismatch(
    cls_object_data, object_data
):
    @dataclass
    class Alphabet(dict_model.DictModel):
        letter: str

    Alphabet.object_data = cls_object_data
    with pytest.raises(dict_model.DictModel.MismatchedObjectDataFormat):
        Alphabet.init(object_data)


def test_dict_model_init_raises_error_if_object_data_in_invalid_format():
    @dataclass
    class Band(dict_model.DictModel):
        name: str

    with pytest.raises(dict_model.DictModel.MismatchedObjectDataFormat):
        Band.init(object_data="Fugazi")


def test_dict_model_init_raises_error_if_model_has_been_init_already(example_model):
    with pytest.raises(dict_model.DictModel.AlreadyInitialized):
        example_model.init()


def test_dict_model_init_allows_reinitializing_if_specified(example_model):
    example_model.init(object_data={1: {"foo": "yay"}}, force=True)
    assert example_model.object_lookup == {1: example_model(id=1, foo="yay")}


def test_dict_model_declare_object_with_decorator(example_model):
    related_obj = example_model(id=666, foo="bar")

    @example_model.object
    class Boo(example_model):
        foo = "hello"
        related = related_obj

        def report(self):
            return f"foo: {self.foo!r}"

        def custom(self):
            return "Not found anywhere else!"

    assert list(example_model.object_lookup.keys()) == [1]
    obj = example_model.object_lookup[1]

    assert obj == example_model(id=1, foo="hello", active=True, related=related_obj)

    assert obj.standard() == "This is standardized."
    assert obj.report() == "foo: 'hello'"
    assert obj.custom() == "Not found anywhere else!"


def test_dict_model_field_names_returns_field_names(example_model):
    assert example_model.field_names == ["active", "foo", "id", "related"]


def test_dict_model_other_attribute_names_returns_other_attribute_names(example_model):
    assert example_model.other_attribute_names == ["report", "standard"]


def test_dict_model_get_custom_attributes_of_child(
    example_model,
):
    class Whoo(example_model):
        def whoo(self):
            pass

    assert example_model.get_custom_attributes_of_child(Whoo) == ["whoo"]


def test_dict_model_pk_attribute_returns_id(example_model):
    example = example_model(id=1, foo="bar")
    assert example.pk == 1


def test_dict_model_snake_case_handles_pascal_case():
    assert dict_model.DictModel.snake_case("HelloWorld") == "hello_world"


def test_dict_model_snake_case_handles_spaces():
    assert dict_model.DictModel.snake_case("Hello World") == "hello_world"


def test_dict_model_from_dict(example_model):
    example_model.init({2: {"foo": "boo"}}, force=True)

    example = example_model.from_dict(
        {"id": 1, "foo": "bar", "related": {"dict_model_name": "Example", "id": 2}}
    )
    assert example == example_model(
        id=1, foo="bar", related=example_model(id=2, foo="boo")
    )


def test_dict_model_from_dict_raises_error_with_custom_fields(example_model):
    with pytest.raises(dict_model.DictModel.CannotDeserializeCustomAttributes):
        example_model.from_dict({"id": 1, "foo": "bar", "custom": "invalid"})


def test_dict_model_save_adds_to_object_lookup(example_model):
    example = example_model(id=1, foo="bar")
    example.save()
    assert example_model.object_lookup == {1: example}


def test_dict_model_save_overwrites_existing_data(example_model):
    example_model.init({1: {"foo": "bar", "active": True}}, force=True)
    example = example_model(id=1, foo="baz", active=False)
    example.save()
    assert example_model.object_lookup == {1: example}


def test_dict_model_save_assigns_id_if_none_provided(example_model):
    example_model.init({1: {"foo": "bar"}}, force=True)
    example2 = example_model(foo="baz", active=False)
    example2.save()
    assert example2.id == 2
    assert example_model.object_lookup == {
        1: example_model(id=1, foo="bar"),
        2: example_model(id=2, foo="baz", active=False),
    }


def test_dict_model_save_defaults_id_to_1(example_model):
    example = example_model(foo="baz")
    example.save()
    assert example.id == 1
    assert example_model.object_lookup == {1: example}


def test_dict_model_delete_removes_instance_from_object_lookup(example_model):
    example_model.init({1: {"foo": "bar"}}, force=True)
    example = example_model(id=1, foo="bar")
    example.delete()
    assert example_model.object_lookup == {}


def test_dict_model_delete_raises_error_if_not_persisted(example_model):
    example = example_model(foo="bar")
    with pytest.raises(dict_model.DictModel.NotPersisted):
        example.delete()


def test_dict_model_to_dict(example_model):
    related = example_model(id=2, foo="boo", active=False)
    example = example_model(id=1, foo="bar", related=related)
    assert example.to_dict() == {
        "id": 1,
        "foo": "bar",
        "active": True,
        "related": dict_model.serializers.dict_model(related),
    }


def test_dict_model_to_dict_ignores_custom_attributes(example_model):
    example = example_model(id=1, foo="bar")
    example.custom = lambda _: "this won't serialize!"
    assert "custom" not in example.to_dict()


def test_dict_model_from_json_file_identifies_model_and_initializes_data(
    example_model,
):
    @dataclass
    class OtherModel(dict_model.DictModel):
        name: str

        object_data = {1: {"name": "hello"}}

    OtherModel.init()

    json_data = {
        "dict_model_name": "Example",
        "object_data": {
            "1": {"foo": "bar", "active": False},
            "2": {
                "foo": "baz",
                "active": True,
                "related": {"dict_model_name": "OtherModel", "id": 1},
            },
        },
    }

    (TEST_FILES / "test.json").write_text(json.dumps(json_data))

    dict_model.DictModel.from_json_file(TEST_FILES / "test.json", force=True)

    assert example_model.object_lookup == {
        1: example_model(id=1, foo="bar", active=False, related=None),
        2: example_model(
            id=2, foo="baz", active=True, related=OtherModel(id=1, name="hello")
        ),
    }


def test_dict_model_from_json_file_initializes_data_for_specific_model_without_name(
    example_model,
):
    @dataclass
    class OtherModel(dict_model.DictModel):
        name: str

        object_data = {1: {"name": "hello"}}

    OtherModel.init()

    json_data = {
        "object_data": {
            "1": {"foo": "bar", "active": False},
            "2": {
                "foo": "baz",
                "active": True,
                "related": {"dict_model_name": "OtherModel", "id": 1},
            },
        },
    }

    (TEST_FILES / "test.json").write_text(json.dumps(json_data))

    example_model.from_json_file(TEST_FILES / "test.json", force=True)

    assert example_model.object_lookup == {
        1: example_model(id=1, foo="bar", active=False, related=None),
        2: example_model(
            id=2, foo="baz", active=True, related=OtherModel(id=1, name="hello")
        ),
    }


def test_dict_model_from_json_file_raises_error_if_no_model_is_specified(
    example_model,
):
    @dataclass
    class OtherModel(dict_model.DictModel):
        name: str

        object_data = {1: {"name": "hello"}}

    OtherModel.init()

    json_data = {
        "object_data": {
            "1": {"foo": "bar", "active": False},
            "2": {
                "foo": "baz",
                "active": True,
                "related": {"dict_model_name": "OtherModel", "id": 1},
            },
        },
    }

    (TEST_FILES / "test.json").write_text(json.dumps(json_data))

    with pytest.raises(dict_model.DictModel.NoModelSpecified):
        dict_model.DictModel.from_json_file(TEST_FILES / "test.json", force=True)


def test_dict_model_from_json_file_raises_error_if_invalid_model_is_specified(
    example_model,
):
    @dataclass
    class OtherModel(dict_model.DictModel):
        name: str

        object_data = {1: {"name": "hello"}}

    OtherModel.init()

    json_data = {
        "dict_model_name": "INVALID",
        "object_data": {
            "1": {"foo": "bar", "active": False},
            "2": {
                "foo": "baz",
                "active": True,
                "related": {"dict_model_name": "OtherModel", "id": 1},
            },
        },
    }

    (TEST_FILES / "test.json").write_text(json.dumps(json_data))

    with pytest.raises(DictModelNotFound):
        dict_model.DictModel.from_json_file(TEST_FILES / "test.json", force=True)


def test_dict_model_from_json_file_raises_error_if_model_in_json_does_not_match(
    example_model,
):
    @dataclass
    class OtherModel(dict_model.DictModel):
        name: str

        object_data = {1: {"name": "hello"}}

    OtherModel.init()

    json_data = {
        "dict_model_name": "OtherModel",
        "object_data": {
            "1": {"foo": "bar", "active": False},
            "2": {
                "foo": "baz",
                "active": True,
                "related": {"dict_model_name": "OtherModel", "id": 1},
            },
        },
    }

    (TEST_FILES / "test.json").write_text(json.dumps(json_data))

    with pytest.raises(example_model.SpecifiedModelsDoNotMatch):
        example_model.from_json_file(TEST_FILES / "test.json", force=True)


def test_dict_model_from_json_file_raises_error_if_model_already_init_and_not_forced(
    example_model,
):
    @dataclass
    class OtherModel(dict_model.DictModel):
        name: str

        object_data = {1: {"name": "hello"}}

    OtherModel.init()

    json_data = {
        "object_data": {
            "1": {"foo": "bar", "active": False},
            "2": {
                "foo": "baz",
                "active": True,
                "related": {"dict_model_name": "OtherModel", "id": 1},
            },
        },
    }

    (TEST_FILES / "test.json").write_text(json.dumps(json_data))

    with pytest.raises(dict_model.DictModel.AlreadyInitialized):
        example_model.from_json_file(TEST_FILES / "test.json")


def test_dict_model_to_json_file(example_model):
    @dataclass
    class OtherModel(dict_model.DictModel):
        name: str

    example_model.init(
        {
            1: {"foo": "bar", "related": OtherModel(id=2, name="hello")},
            2: {"foo": "baz", "active": False},
        },
        force=True,
    )

    example_model.to_json_file(TEST_FILES / "test.json")
    data = json.loads((TEST_FILES / "test.json").read_text())
    assert data == {
        "dict_model_name": "Example",
        "object_data": {
            "1": {
                "id": 1,
                "foo": "bar",
                "active": True,
                "related": {"dict_model_name": "OtherModel", "id": 2},
            },
            "2": {"id": 2, "foo": "baz", "active": False, "related": None},
        },
    }


def test_dict_model_to_json_file_does_not_include_model_name_when_specified(
    example_model,
):
    @dataclass
    class OtherModel(dict_model.DictModel):
        name: str

    example_model.init(
        {
            1: {"foo": "bar", "related": OtherModel(id=2, name="hello")},
            2: {"foo": "baz", "active": False},
        },
        force=True,
    )

    example_model.to_json_file(TEST_FILES / "test.json", specify_model=False)
    data = json.loads((TEST_FILES / "test.json").read_text())
    assert data == {
        "object_data": {
            "1": {
                "id": 1,
                "foo": "bar",
                "active": True,
                "related": {"dict_model_name": "OtherModel", "id": 2},
            },
            "2": {"id": 2, "foo": "baz", "active": False, "related": None},
        },
    }


def test_dict_model_objects_returns_an_object_manager_for_the_class(example_model):
    assert example_model.objects == dict_model.DictModelObjectManager(example_model)


def test_dict_model_objects_can_be_a_custom_object_manager():
    class CustomObjectManager(dict_model.DictModelObjectManager):
        def funky(self, id):
            obj = self.get(id=id)
            return f"get funky: {obj.name}"

    @dataclass
    class CustomManagement(dict_model.DictModel):
        objects = CustomObjectManager()

        name: str

        object_data = {
            1: {"id": 1, "name": "monkey"}
        }

    CustomManagement.init()
    assert CustomManagement.objects.funky(1) == "get funky: monkey"

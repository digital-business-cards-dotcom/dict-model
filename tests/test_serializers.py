from dataclasses import dataclass

import pytest

import dict_models


def test_dict_model_serializer():
    @dataclass
    class Foo(dict_models.DictModel):
        bar: bool

    foo = Foo(id=1, bar=True)
    assert dict_models.serializers.dict_model(foo) == {
        "dict_model_name": "Foo",
        "id": 1,
    }


def test_dict_model_serialzier_raises_error_without_id():
    @dataclass
    class Bar(dict_models.DictModel):
        foo: bool

    bar = Bar(id=None, foo=True)
    with pytest.raises(dict_models.DictModel.NotPersisted):
        dict_models.serializers.dict_model(bar)

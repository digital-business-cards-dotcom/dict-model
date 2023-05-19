from dataclasses import dataclass
from datetime import datetime

import pytest

import dict_model


def test_datetime_serializer(freezer):
    freezer.move_to('2023-01-01')
    assert dict_model.serializers.datetime(datetime.utcnow()) == "2023-01-01T00:00:00"


def test_dict_model_serializer():
    @dataclass
    class Foo(dict_model.DictModel):
        bar: bool

    foo = Foo(id=1, bar=True)
    assert dict_model.serializers.dict_model(foo) == {
        "dict_model_name": "Foo",
        "id": 1,
    }


def test_dict_model_serialzier_raises_error_without_id():
    @dataclass
    class Bar(dict_model.DictModel):
        foo: bool

    bar = Bar(id=None, foo=True)
    with pytest.raises(dict_model.DictModel.NotPersisted):
        dict_model.serializers.dict_model(bar)

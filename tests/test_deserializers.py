from dataclasses import dataclass
from datetime import datetime

import dict_model


def test_datetime_deserialzier():
    assert dict_model.deserializers.datetime("2023-01-01T00:00:00") == datetime(
        2023, 1, 1
    )


def test_dict_model_deserializer():
    @dataclass
    class Bar(dict_model.DictModel):
        foo: bool

        object_data = {2: {"foo": True}}

    Bar.init()

    data = {"dict_model_name": "Bar", "id": 2}
    assert dict_model.deserializers.dict_model(data) == Bar(id=2, foo=True)

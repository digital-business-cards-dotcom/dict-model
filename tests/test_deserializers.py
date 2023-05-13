from dataclasses import dataclass

import dict_model


def test_dict_model_deserializer():
    @dataclass
    class Bar(dict_model.DictModel):
        foo: bool

        object_data = {2: {"foo": True}}

    Bar.init()

    data = {"dict_model_name": "Bar", "id": 2}
    assert dict_model.deserializers.dict_model(data) == Bar(id=2, foo=True)

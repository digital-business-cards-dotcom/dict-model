from dataclasses import dataclass

import dict_models


def test_dict_model_deserializer():
    @dataclass
    class Bar(dict_models.DictModel):
        foo: bool

    bar = Bar(id=2, foo=True)
    Bar._object_lookup = {2: bar}

    data = {"dict_model_name": "Bar", "id": 2}
    assert dict_models.deserializers.dict_model(data) == bar

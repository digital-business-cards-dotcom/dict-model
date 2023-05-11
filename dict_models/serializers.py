DICT_MODEL_CLASSES = {}


def dict_model(value) -> dict:
    if value.id is None:
        raise value.NotPersisted(str(value))
    return {"dict_model_name": value.__class__.__name__, "id": value.id}

from .serializers import DICT_MODEL_CLASSES


def dict_model(value):
    dict_model_cls = DICT_MODEL_CLASSES[value["dict_model_name"]]
    return dict_model_cls.objects.get(id=value["id"])

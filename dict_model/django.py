import typing

from django.db import models

from . import DictModel
from .lookup import get_dict_model_class

UNSET = "__UNSET__"


class DictModelField(models.IntegerField):
    def __init__(
        self,
        dict_model_class: typing.Union[typing.Type[DictModel], str],
        choices: typing.Optional[typing.List[typing.Tuple]] = UNSET,
        *args,
        **kwargs
    ):
        if isinstance(dict_model_class, str):
            dict_model_class = get_dict_model_class(dict_model_class)
        if not dict_model_class.has_been_initialized:
            dict_model_class.init()
        self._dict_model_class = dict_model_class
        if choices == UNSET:
            kwargs["choices"] = DictModelField.get_choices_for_dict_model_class(
                dict_model_class
            )
        else:
            kwargs["choices"] = choices
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_choices_for_dict_model_class(dict_model_class: typing.Type[DictModel]):
        return [(obj.id, obj.name) for obj in dict_model_class.objects.all()]

    @property
    def non_db_attrs(self):
        return super().non_db_attrs + ("_dict_model_class")

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        args = [self._dict_model_class.__name__] + args
        return name, path, args, kwargs

    def from_db_value(
        self, value: typing.Any, *args, **kwargs
    ) -> typing.Optional[DictModel]:
        if value is None:
            return value
        return self._dict_model_class.objects.get(id=int(value))

    def get_prep_value(self, value: typing.Any) -> int:
        try:
            return value.id
        except AttributeError:
            return int(value)

    def to_python(self, value: typing.Any) -> typing.Optional[DictModel]:
        if isinstance(value, self._dict_model_class):
            return value

        if value is None:
            return value

        return self._dict_model_class.objects.get(id=int(value))

import typing
from django.db import models
from . import DictModel


UNSET = "__UNSET__"


class DictModelField(models.IntegerField):
    def __init__(
        self,
        dict_model_class: typing.Type[DictModel],
        choices: typing.Optional[typing.List[typing.Tuple]] = UNSET,
        *args,
        **kwargs
    ):
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

    def from_db_value(
        self, value: typing.Any, *args, **kwargs
    ) -> typing.Optional[DictModel]:
        if value is None:
            return value
        return self._dict_model_class.objects.get(id=int(value))

    def get_prep_value(self, value: typing.Any) -> int:
        return value.id

    def to_python(self, value: typing.Any) -> typing.Optional[DictModel]:
        if isinstance(value, self._dict_model_class):
            return value

        if value is None:
            return value

        return self._dict_model_class.objects.get(id=int(value))

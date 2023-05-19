import typing
from collections import UserList

if typing.TYPE_CHECKING:
    from . import DictModel


class DictModelQuerySet(UserList):
    class DoesNotExist(Exception):
        pass

    class MultipleResultsFound(Exception):
        pass

    class NoDictModelProvided(Exception):
        pass

    def __init__(
        self,
        data: typing.Optional[list] = None,
        dict_model_class: typing.Optional[type["DictModel"]] = None,
    ) -> None:
        data = data or []
        if not dict_model_class:
            try:
                dict_model_class = data[0].__class__
            except IndexError:
                raise DictModelQuerySet.NoDictModelProvided()
        self._dict_model_class = dict_model_class
        self.data = data

    def all(self):
        return self

    def create(self, **kwargs) -> "DictModel":
        obj = self._dict_model_class(**kwargs)
        obj.save()
        return obj

    def exclude(self, **kwargs) -> "DictModelQuerySet":
        return DictModelQuerySet(
            [obj for obj in self.data if not self._passes_filters(obj, **kwargs)],
            dict_model_class=self._dict_model_class,
        )

    def first(self) -> "DictModelQuerySet":
        try:
            return self.data[0]
        except IndexError:
            return None

    def filter(self, **kwargs) -> "DictModelQuerySet":
        return DictModelQuerySet(
            [obj for obj in self.data if self._passes_filters(obj, **kwargs)],
            dict_model_class=self._dict_model_class,
        )

    def get(self, **kwargs) -> "DictModel":
        result = None
        for obj in self.data:
            if self._passes_filters(obj, **kwargs):
                if result:
                    raise DictModelQuerySet.MultipleResultsFound(str(kwargs))
                result = obj

        if not result:
            raise DictModelQuerySet.DoesNotExist(str(kwargs))

        return result

    def last(self) -> "DictModel":
        try:
            return self.data[-1]
        except IndexError:
            return None

    @staticmethod
    def _passes_filters(obj, **filters) -> bool:
        for field, value in filters.items():
            if field.endswith("__in"):
                field, *_ = field.split("__in")
                if getattr(obj, field) not in value:
                    return False
            elif getattr(obj, field) != value:
                return False
        return True

    def order_by(self, field: str) -> "DictModelQuerySet":
        if field.startswith("-"):
            field = field[1:]
            reverse = True
        else:
            reverse = False
        return DictModelQuerySet(
            sorted(self.data, key=lambda obj: getattr(obj, field), reverse=reverse),
            dict_model_class=self._dict_model_class,
        )

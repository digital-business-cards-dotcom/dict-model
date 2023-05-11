from collections import UserList


class DictModelQuerySet(UserList):
    class DoesNotExist(Exception):
        pass

    class MultipleResultsFound(Exception):
        pass

    class NoDictModelProvided(Exception):
        pass

    def __init__(self, data=None, dict_model_class=None):
        data = data or []
        if not dict_model_class:
            try:
                dict_model_class = data[0].__class__
            except IndexError:
                raise DictModelQuerySet.NoDictModelProvided()
        self._dict_model_class = dict_model_class
        self.data = data

    def create(self, **kwargs):
        obj = self._dict_model_class(**kwargs)
        obj.save()
        return obj

    def exclude(self, **kwargs):
        return DictModelQuerySet(
            [obj for obj in self.data if not self._passes_filters(obj, **kwargs)],
            dict_model_class=self._dict_model_class,
        )

    def first(self):
        try:
            return self.data[0]
        except IndexError:
            return None

    def filter(self, **kwargs):
        return DictModelQuerySet(
            [obj for obj in self.data if self._passes_filters(obj, **kwargs)],
            dict_model_class=self._dict_model_class,
        )

    def get(self, **kwargs):
        result = None
        for obj in self.data:
            if self._passes_filters(obj, **kwargs):
                if result:
                    raise DictModelQuerySet.MultipleResultsFound(str(kwargs))
                result = obj

        if not result:
            raise DictModelQuerySet.DoesNotExist(str(kwargs))

        return result

    def last(self):
        try:
            return self.data[-1]
        except IndexError:
            return None

    @staticmethod
    def _passes_filters(obj, **filters):
        for field, value in filters.items():
            if getattr(obj, field) != value:
                return False
        return True

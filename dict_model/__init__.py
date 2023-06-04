import dataclasses
import functools
import json
import re
import typing
from datetime import datetime
from pathlib import Path

from django.utils.functional import classproperty

from . import deserializers, lookup, serializers
from .query_sets import DictModelQuerySet

__version__ = "0.0.2"


@dataclasses.dataclass
class DictModelObjectManager:
    dict_model_class: typing.Type["DictModel"]

    def all(self) -> "DictModelQuerySet":
        return DictModelQuerySet(
            sorted(
                [obj for obj in self.dict_model_class.object_lookup.values()],
                key=lambda obj: obj.id,
            ),
            dict_model_class=self.dict_model_class,
        )

    def create(self, **kwargs) -> "DictModel":
        obj = self.dict_model_class(**kwargs)
        obj.save()
        return obj

    def exclude(self, **kwargs) -> "DictModelQuerySet":
        return self.all().exclude(**kwargs)

    def first(self) -> typing.Optional["DictModel"]:
        return self.all().first()

    def filter(self, **kwargs) -> "DictModelQuerySet":
        return self.all().filter(**kwargs)

    def get(self, **kwargs) -> "DictModel":
        return self.all().get(**kwargs)

    def last(self, **kwargs) -> typing.Optional["DictModel"]:
        return self.all().last()


@dataclasses.dataclass(kw_only=True)
class DictModel:
    class AlreadyInitialized(Exception):
        pass

    class CannotDeserializeCustomAttributes(Exception):
        pass

    class CannotSerializeCustomAttributes(Exception):
        pass

    class HasNotBeenInitialized(Exception):
        pass

    class NoModelSpecified(Exception):
        pass

    class SpecifiedModelsDoNotMatch(Exception):
        pass

    class MismatchedObjectDataFormat(Exception):
        pass

    class NotPersisted(Exception):
        pass

    id: typing.Optional[int] = None

    @classmethod
    def init(
        cls,
        object_data: typing.Optional[typing.Union[list, dict]] = None,
        force: bool = False,
    ) -> type["DictModel"]:
        if not force and cls.has_been_initialized:
            raise DictModel.AlreadyInitialized(cls.__name__)

        if "objects" not in dir(cls):
            cls.objects = DictModelObjectManager(cls)
        lookup.set_dict_model_class(cls.__name__, cls)

        cls_object_data = getattr(cls, "object_data", None)
        if cls_object_data is None:
            cls_object_data = {}
        else:
            delattr(cls, "object_data")

        if object_data:
            if isinstance(object_data, dict):
                cls_object_data = cls_object_data or {}
                try:
                    object_data = {**cls_object_data, **object_data}
                except TypeError:
                    raise DictModel.MismatchedObjectDataFormat(
                        str(cls_object_data), str(object_data)
                    )
            elif isinstance(object_data, list):
                cls_object_data = cls_object_data or []
                try:
                    object_data = cls_object_data + object_data
                except TypeError:
                    raise DictModel.MismatchedObjectDataFormat(
                        str(cls_object_data), str(object_data)
                    )
        else:
            object_data = cls_object_data

        cls.object_lookup = {}
        if isinstance(object_data, dict):
            for id, data in object_data.items():
                obj = cls.from_dict({**{"id": data.pop("id", id)}, **data})
                cls._save_object_data(cls, obj)
        elif isinstance(object_data, list):
            for idx, data in enumerate(object_data):
                obj = cls.from_dict({**{"id": data.pop("id", idx + 1)}, **data})
                cls._save_object_data(cls, obj)
        else:
            raise DictModel.MismatchedObjectDataFormat(str(object_data))

        cls.set_has_been_initialized(True)
        return cls

    @classmethod
    def from_dict(cls, dict_data: dict) -> "DictModel":
        field_data = {}
        for field, value in dict_data.items():
            if field not in cls.field_names:
                raise DictModel.CannotDeserializeCustomAttributes(field)
            field_data[field] = cls.deserialize(value)
        return cls(**field_data)

    @classmethod
    def object(cls, child: type["DictModel"]) -> "DictModel":
        # TODO: Cleaner way to get non-standard attributes.
        field_data = {field: getattr(child, field, None) for field in cls.field_names}
        obj = cls(**field_data)

        for attr in cls.other_attribute_names + cls.get_custom_attributes_of_child(
            child
        ):
            value = getattr(child, attr, None)
            if not value:
                continue
            if callable(value):
                value = functools.partial(value, obj)
            setattr(obj, attr, value)

        obj.save()
        return obj

    @classmethod
    def get_custom_attributes_of_child(
        cls, other: type["DictModel"]
    ) -> typing.Iterable:
        if isinstance(other, dict):
            other_attrs = list(other.keys())
        else:
            other_attrs = dir(other)

        return sorted(
            [
                attr
                for attr in other_attrs
                if attr not in dir(cls) and attr not in cls.field_names
            ]
        )

    @classmethod
    def from_json_file(cls, path: typing.Union[str, Path], **kwargs) -> None:
        path = Path(path)
        json_data = json.loads(path.read_text())

        dict_model_name = json_data.get("dict_model_name")
        if cls == DictModel:
            if not dict_model_name:
                raise DictModel.NoModelSpecified()
            dict_model_cls = lookup.get_dict_model_class(dict_model_name)
        else:
            if dict_model_name and dict_model_name != cls.__name__:
                raise DictModel.SpecifiedModelsDoNotMatch(
                    f"{dict_model_name}, {cls.__name__}"
                )
            dict_model_cls = cls

        object_data = json_data["object_data"]
        # Convert JSON string keys into integers.
        if isinstance(object_data, dict):
            object_data = {int(k): v for k, v in object_data.items()}

        dict_model_cls.init(object_data, **kwargs)

    @classmethod
    def to_json_file(
        cls, path: typing.Union[str, Path], specify_model: bool = True
    ) -> None:
        path = Path(path)
        json_data = {
            "object_data": {id: obj.to_dict() for id, obj in cls.object_lookup.items()},
        }
        if specify_model:
            json_data["dict_model_name"] = cls.__name__
        path.write_text(json.dumps(json_data))

    @classproperty
    def has_been_initialized(cls) -> bool:
        return getattr(cls, "_has_been_initialized", False)

    @classmethod
    def set_has_been_initialized(cls, value: bool) -> None:
        cls._has_been_initialized = value

    @classproperty
    def field_names(cls) -> typing.Iterable:
        return sorted([field.name for field in dataclasses.fields(cls)])

    @classproperty
    def other_attribute_names(cls) -> typing.Iterable:
        return sorted(
            list(
                (
                    set(dir(cls))
                    - set(dir(DictModel))
                    - set(cls.field_names)
                    - set(
                        [
                            "_has_been_initialized",
                            "objects",
                            "object_lookup",
                            "object_data",
                        ]
                    )
                )
            )
        )

    @property
    def pk(self) -> typing.Optional[int]:
        return self.id

    @staticmethod
    def deserialize(value: typing.Any) -> typing.Any:
        if isinstance(value, str):
            try:
                return deserializers.datetime(value)
            except ValueError:
                pass
        elif isinstance(value, dict):
            if "dict_model_name" in value:
                return deserializers.dict_model(value)
        return value

    @staticmethod
    def serialize(value: typing.Any) -> typing.Any:
        if isinstance(value, datetime):
            return serializers.datetime(value)
        elif isinstance(value, DictModel):
            return serializers.dict_model(value)
        return value

    @staticmethod
    def snake_case(text: str) -> str:
        return re.sub(r"(?<!^)(?=[A-Z])", "_", text).replace(" ", "").lower()

    def delete(self) -> None:
        try:
            del self.object_lookup[self.id]
        except KeyError:
            raise DictModel.NotPersisted(self.id)

    def save(self) -> None:
        self._save_object_data(self.__class__, self)

    @staticmethod
    def _save_object_data(model, obj) -> None:
        if not model.has_been_initialized:
            model.init()

        if obj.id is None:
            if model.object_lookup:
                obj.id = max(model.object_lookup.keys()) + 1
            else:
                obj.id = 1

        model.object_lookup[obj.id] = obj

        # When available, set a constant for quick lookup, based on the `name` attribute
        try:
            lookup_constant = model.snake_case(obj.name).upper()
            if not hasattr(model, lookup_constant):
                setattr(model, lookup_constant, obj)
        except AttributeError:
            pass

    def to_dict(self) -> dict:
        if self.__class__.get_custom_attributes_of_child(self):
            raise DictModel.CannotSerializeCustomAttributes(str(self))

        return {
            field: DictModel.serialize(getattr(self, field))
            for field in self.__class__.field_names
        }

import re
import dataclasses
import functools
import json
import typing
from pathlib import Path

from django.utils.functional import classproperty

from . import deserializers, serializers
from .query_sets import DictModelQuerySet

__version__ = "0.0.1"


@dataclasses.dataclass(kw_only=True)
class DictModel:
    class CannotDeserializeCustomAttributes(Exception):
        pass

    class CannotSerializeCustomAttributes(Exception):
        pass

    class NoModelSpecified(Exception):
        pass

    class SpecifiedModelsDoNotMatch(Exception):
        pass

    class MismatchedObjectDataFormat(Exception):
        pass

    class NotPersisted(Exception):
        pass

    class UnknownModelSpecified(Exception):
        pass

    id: typing.Optional[int] = None

    @classmethod
    def init(
        cls, object_data: typing.Optional[typing.Union[list, dict]] = None
    ) -> type["DictModel"]:
        if cls.__name__ not in serializers.DICT_MODEL_CLASSES:
            serializers.DICT_MODEL_CLASSES[cls.__name__] = cls

        cls_object_data = getattr(cls, "object_data", None)
        if cls_object_data is not None:
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

        cls._object_lookup = {}
        if not object_data:
            return cls

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
    def from_json_file(cls, path: typing.Union[str, Path]) -> None:
        path = Path(path)
        json_data = json.loads(path.read_text())

        dict_model_name = json_data.get("dict_model_name")
        if cls == DictModel:
            if not dict_model_name:
                raise DictModel.NoModelSpecified()
            try:
                dict_model_cls = serializers.DICT_MODEL_CLASSES[dict_model_name]
            except KeyError:
                raise DictModel.UnknownModelSpecified(dict_model_name)
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

        dict_model_cls.init(object_data)

    @classmethod
    def to_json_file(
        cls, path: typing.Union[str, Path], specify_model: bool = True
    ) -> None:
        path = Path(path)
        json_data = {
            "object_data": {
                id: obj.to_dict() for id, obj in cls._object_lookup.items()
            },
        }
        if specify_model:
            json_data["dict_model_name"] = cls.__name__
        path.write_text(json.dumps(json_data))

    @classproperty
    def objects(cls) -> "DictModelQuerySet":
        return DictModelQuerySet(
            [obj for obj in cls._object_lookup.values()],
            dict_model_class=cls,
        )

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
                    - set(["_object_lookup", "object_data"])
                )
            )
        )

    @property
    def pk(self) -> typing.Optional[int]:
        return self.id

    @staticmethod
    def _snake_case(pascal_case: str) -> str:
        return re.sub(r"(?<!^)(?=[A-Z])", "_", pascal_case).lower()

    @staticmethod
    def _save_object_data(model, obj) -> None:
        if obj.id is None:
            if model._object_lookup:
                obj.id = max(model._object_lookup.keys()) + 1
            else:
                obj.id = 1

        model._object_lookup[obj.id] = obj

        # When available, set a constant for quick lookup, based on the `name` attribute
        try:
            lookup_constant = model._snake_case(obj.name).upper()
            if not hasattr(model, lookup_constant):
                setattr(model, lookup_constant, obj)
        except AttributeError:
            pass

    @staticmethod
    def serialize(value: typing.Any) -> typing.Any:
        if isinstance(value, DictModel):
            return serializers.dict_model(value)
        return value

    @staticmethod
    def deserialize(value: typing.Any) -> typing.Any:
        if isinstance(value, dict):
            if "dict_model_name" in value:
                return deserializers.dict_model(value)
        return value

    def delete(self) -> None:
        try:
            del self._object_lookup[self.id]
        except KeyError:
            raise DictModel.NotPersisted(self.id)

    def save(self) -> None:
        self._save_object_data(self.__class__, self)

    def to_dict(self) -> dict:
        if self.__class__.get_custom_attributes_of_child(self):
            raise DictModel.CannotSerializeCustomAttributes(str(self))

        return {
            field: DictModel.serialize(getattr(self, field))
            for field in self.__class__.field_names
        }
from typing import Dict, List, Type, get_origin, get_args, Union
from pydantic import BaseModel, EmailStr
from pydantic._internal._model_construction import PydanticModelField
from pydantic.v1 import BaseSettings
from pydantic_core import PydanticUndefined

from .base import FieldMeta


class ModelToolsPydantic:
    PYDANTIC_FIELD_MAPPING = {
        str: "string",
        int: "int",
        float: "float",
        bool: "bool",
        EmailStr: "email",
    }

    @staticmethod
    def is_model_class(cls) -> bool:
        return isinstance(cls, type) and issubclass(cls, BaseModel)

    @staticmethod
    def is_model_instance(obj) -> bool:
        return isinstance(obj, BaseModel)

    @staticmethod
    def is_settings_instance(obj) -> bool:
        return isinstance(obj, BaseSettings)

    @staticmethod
    def is_settings_class(cls) -> bool:
        return isinstance(cls, type) and issubclass(cls, BaseSettings)

    @staticmethod
    def extract_actual_type(field: PydanticModelField) -> Type:
        """
        Extracts the actual type from a Pydantic ModelField, handling Optional and Union types.

        :param field: The Pydantic ModelField object.
        :return: The actual type of the field.
        """
        annotation = field.annotation
        origin = get_origin(annotation)
        args = get_args(annotation)
        if origin is Union:
            non_none = [arg for arg in args if arg is not type(None)]
            return non_none[0] if len(non_none) == 1 else annotation
        return annotation

    @staticmethod
    def extract_fields_from_model(model: Type[BaseModel], exclude: List[str], readonly: List[str]) -> Dict[str, FieldMeta]:
        fields = {}
        for name, field in model.model_fields.items():
            if name in exclude:
                continue
            default = None if field.default is PydanticUndefined else field.default
            description = None
            if hasattr(field, "field_info") and hasattr(field.field_info, "description"):
                description = field.field_info.description
            elif hasattr(field, "description"):
                description = field.description

            fields[name] = FieldMeta(
                type=ModelToolsPydantic.extract_actual_type(field),
                required=field.default is PydanticUndefined and field.default_factory is None,
                readonly=name in readonly,
                default=default,
                description=description,
            )
        return fields

    @staticmethod
    def extract_fields_from_settings(model: Type[BaseSettings], exclude: List[str], readonly: List[str]) -> Dict[str, FieldMeta]:
        fields = {}
        for name, field in model.__fields__.items():
            if name in exclude:
                continue
            default = None if field.default is PydanticUndefined else field.default
            fields[name] = FieldMeta(
                type=field.outer_type_,
                required=field.required,
                readonly=name in readonly,
                default=default,
                description=field.field_info.description,
            )
        return fields

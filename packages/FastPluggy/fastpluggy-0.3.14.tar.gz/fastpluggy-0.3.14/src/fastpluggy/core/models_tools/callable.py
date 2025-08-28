# model_tools/callable.py
import inspect
from typing import get_type_hints, Annotated, Any, Dict, get_origin, get_args

from .base import FieldMeta
from ..tools.inspect_tools import is_internal_dependency


class ModelToolsCallable:
    CALLABLE_FIELD_MAPPING = {
        str: "string",
        int: "int",
        float: "float",
        bool: "bool",
        list: "text",
    }

    @staticmethod
    def extract_fields_from_callable(func, exclude: list[str], readonly: list[str]) -> Dict[str, FieldMeta]:
        sig = inspect.signature(func)
        hints = get_type_hints(func, include_extras=True)
        fields = {}

        for name, param in sig.parameters.items():
            if name in exclude:
                continue

            annotation = hints.get(name, str)

            if is_internal_dependency(annotation):
                continue

            if get_origin(annotation) is Annotated:
                args = get_args(annotation)
                annotation = next((a for a in args if not is_internal_dependency(a)), str)

            required = param.default == inspect.Parameter.empty
            default = None if required else param.default

            fields[name] = FieldMeta(
                type=annotation,
                required=required,
                readonly=name in readonly,
                default=default,
                description=None
            )
        return fields

    @staticmethod
    def get_model_metadata(func, exclude: list[str] = None, readonly: list[str] = None) -> Dict[str, Dict[str, Any]]:
        exclude = exclude or []
        readonly = readonly or []

        fields = ModelToolsCallable.extract_fields_from_callable(func, exclude, readonly)

        for meta in fields.values():
            if isinstance(meta.type, (str, type)):
                meta.type = ModelToolsCallable.CALLABLE_FIELD_MAPPING.get(meta.type, "string")

        return {k: v.to_dict() for k, v in fields.items()}

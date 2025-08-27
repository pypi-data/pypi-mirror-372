# models_tools/shared.py
from typing import Dict, Any, List, Optional

from .sqlalchemy import ModelToolsSQLAlchemy
from .pydantic import ModelToolsPydantic
from .base import FieldMeta


class ModelToolsShared:

    @staticmethod
    def _resolve_model_type(model_or_instance):
        if ModelToolsSQLAlchemy.is_sqlalchemy(model_or_instance):
            return "sqlalchemy"
        if ModelToolsPydantic.is_model_class(model_or_instance) or ModelToolsPydantic.is_model_instance(
                model_or_instance):
            return "pydantic"
        if ModelToolsPydantic.is_settings_class(model_or_instance):
            return "basesettings"
        if ModelToolsPydantic.is_settings_instance(model_or_instance):
            return "basesettings_instance"
        if isinstance(model_or_instance, list) and model_or_instance and isinstance(model_or_instance[0], dict):
            return "dict_list"
        if isinstance(model_or_instance, dict):
            return "raw_dict"
        if callable(model_or_instance):
            return "callable"
        raise TypeError(f"Unsupported model or instance type : {type(model_or_instance)} ")

    @staticmethod
    def get_model_metadata(model, exclude_fields: Optional[List[str]] = None,
                           readonly_fields: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
        exclude = exclude_fields or []
        readonly = readonly_fields or []

        kind = ModelToolsShared._resolve_model_type(model)

        if kind == "sqlalchemy":
            fields = ModelToolsSQLAlchemy.extract_fields(model, exclude, readonly)
            mapping = ModelToolsSQLAlchemy.SQLALCHEMY_FIELD_MAPPING

        elif kind in ("pydantic", "basesettings", "basesettings_instance"):
            extractor = ModelToolsPydantic.extract_fields_from_model if kind == "pydantic" else ModelToolsPydantic.extract_fields_from_settings
            fields = extractor(model, exclude, readonly)
            mapping = ModelToolsPydantic.PYDANTIC_FIELD_MAPPING

        elif kind == "dict_list":
            fields = {
                key: FieldMeta(
                    type=type(value).__name__,
                    required=False,
                    readonly=key in readonly,
                    default=value,
                )
                for key, value in model[0].items() if key not in exclude
            }
            mapping = ModelToolsPydantic.PYDANTIC_FIELD_MAPPING

        elif kind == "callable":
            from .callable import ModelToolsCallable
            fields = ModelToolsCallable.extract_fields_from_callable(model, exclude, readonly)
            mapping = ModelToolsCallable.CALLABLE_FIELD_MAPPING
        else:
            raise TypeError(f"Unsupported model type. (kind: {kind})")

        for meta in fields.values():
            if isinstance(meta.type, (str, type)):
                meta.type = mapping.get(meta.type, "string")

        return {k: v.to_dict() for k, v in fields.items()}

    @staticmethod
    def extract_model_data(instance, fields: Optional[List[str]] = None, exclude: Optional[List[str]] = None) -> Dict[
        str, Any]:
        kind = ModelToolsShared._resolve_model_type(instance)

        if kind == "raw_dict":
            data = instance
        elif kind == "pydantic":
            data = instance.model_dump()
        elif kind == "sqlalchemy":
            data = ModelToolsSQLAlchemy.model_to_dict(instance, exclude)
        elif kind == "basesettings_instance":
            data = instance.dict()
        else:
            raise ValueError("Unsupported instance for data extraction")

        if fields:
            return {key: data[key] for key in fields if key in data}
        return {key: val for key, val in data.items() if key not in (exclude or [])}

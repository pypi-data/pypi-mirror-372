import logging
import random
from abc import ABC
from abc import abstractmethod
from inspect import signature, _empty
from typing import Any, List, Dict, Callable
from typing import Tuple, Type

from pydantic import BaseModel
from pydantic import create_model

from fastpluggy.core.global_registry import GlobalRegistry


def config_model_from_init(
    view_cls: Type,
) -> Type[BaseModel]:
    sig = signature(view_cls)
    fields: Dict[str, Tuple[Any, Any]] = {}

    # skip 'self'
    for name, param in sig.parameters.items():
        ann = param.annotation if param.annotation is not _empty else Any
        default = param.default if param.default is not _empty else ...
        fields[name] = (ann, default)

    model_name = f"{view_cls.__name__}Config"
    return create_model(model_name, **fields)




class FieldHandlingView(ABC):
    """
    Abstract base class for components that handle field processing.
    """

    @staticmethod
    def get_field_name(field: Any) -> str:
        """
        Extract the field name from various field representations.

        Args:
            field (Any): The field representation (string, SQLAlchemy field, etc.).

        Returns:
            str: The extracted field name.

        Raises:
            ValueError: If the field type is unsupported.
        """
        if isinstance(field, str):
            return field
        elif hasattr(field, 'key'):
            return field.key  # SQLAlchemy Column object
        elif hasattr(field, 'fget'):
            return field.fget.__name__  # SQLAlchemy hybrid property
        elif hasattr(field, '__name__'):
            return field.__name__  # Regular property or method
        else:
            raise ValueError(f"Unsupported field type: {field}")

    @staticmethod
    def process_field_callbacks(field_callbacks: dict[Any, Callable[[Any], Any]]) -> dict[Any, Callable[[Any], Any]]:
        """
        Process field_callbacks to ensure keys are field names.
        """
        processed_callbacks = {}
        for key, callback in field_callbacks.items():
            field_name = FieldHandlingView.get_field_name(key)
            processed_callbacks[field_name] = callback
        return processed_callbacks

    @staticmethod
    def process_fields_names(list_fields: List[Any]) -> List[str]:
        """
        Process exclude_fields to ensure they are field names.

        Args:
            list_fields (List[Any]): A list of field names or SQLAlchemy field references.

        Returns:
            List[str]: A list of processed field names.
        """
        return [FieldHandlingView.get_field_name(field) for field in list_fields]



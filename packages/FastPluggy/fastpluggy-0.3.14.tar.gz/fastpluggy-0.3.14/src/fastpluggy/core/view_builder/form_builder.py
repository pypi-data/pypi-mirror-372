# form_builder.py
from typing import Type, Dict, Any, List, Optional

from wtforms import (
    Form,
    StringField,
    SelectField,
    IntegerField,
    FloatField,
    RadioField,
    BooleanField,
    Field
)
from wtforms.fields.datetime import DateField
from wtforms.fields.simple import HiddenField, EmailField, TextAreaField, FileField
from wtforms.validators import DataRequired, Optional as ValidatorOptional

from fastpluggy.core.models_tools.shared import ModelToolsShared

FORM_FIELD_MAPPING = {
    "string": StringField,
    "text": TextAreaField,
    "int": IntegerField,
    "float": FloatField,
    "bool": BooleanField,
    "date": DateField,
    "datetime": DateField, #DateTimeField,
    "enum": SelectField,
    "radio": RadioField,
    "email": EmailField,
    "file": FileField,
}


class FormBuilder:
    @staticmethod
    def generate_form(
        model: Type,
        exclude_fields: Optional[List[str]] = None,
        additional_fields: Optional[Dict[str, Field]] = None,
        field_widgets: Optional[Dict[str, Any]] = None,
        field_render_kw: Optional[Dict[str, Dict[str, Any]]] = None,
        readonly_fields: Optional[List[str]] = None,
    ) -> Type[Form]:
        """
        Generates a WTForms Form class based on a SQLAlchemy or Pydantic model.

        :param model: The model class to generate the form from.
        :param exclude_fields: A list of field names to exclude entirely.
        :param additional_fields: A dictionary of additional fields to include in the form.
        :param field_widgets: A dictionary mapping field names to custom widgets.
        :param field_render_kw: A dictionary mapping field names to render keyword arguments.
        :param readonly_fields: A list of field names to render as read-only.
        :return: A WTForms Form class.
        """
        exclude_fields = exclude_fields or []
        readonly_fields = readonly_fields or []

        fields_metadata = ModelToolsShared.get_model_metadata(model, exclude_fields, readonly_fields)

        # Create form attributes using the factory method
        attributes = FormBuilder.create_form_attributes(
            fields_metadata=fields_metadata,
            field_widgets=field_widgets,
            field_render_kw=field_render_kw,
        )

        # Add any additional fields if supplied
        if additional_fields:
            attributes.update(additional_fields)

        # Decide on a name for the generated Form class
        if hasattr(model, '__name__'):
            model_name = model.__name__
        else:
            model_name = model.__class__.__name__

        # Return a new form class using Python's type(...) dynamic creation
        return type(f"{model_name}Form", (Form,), attributes)

    @staticmethod
    def create_form_attributes(
        fields_metadata: Dict[str, Dict[str, Any]],
        field_widgets: Optional[Dict[str, Any]] = None,
        field_render_kw: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> Dict[str, Field]:
        """
        Create WTForms attributes (field definitions) from field metadata, using a factory method.

        :param fields_metadata: Metadata for the fields to include in the form.
        :param field_widgets: Custom widgets for fields, keyed by field name.
        :param field_render_kw: Render keyword arguments, keyed by field name.
        :return: A dictionary { field_name -> WTForms Field } for building a Form class.
        """
        attributes = {}
        field_widgets = field_widgets or {}
        field_render_kw = field_render_kw or {}

        for field_name, metadata in fields_metadata.items():
            # Render_kw might contain placeholders, classes, user overrides, etc.
            render_kw_for_field = field_render_kw.get(field_name, {})
            widget = field_widgets.get(field_name)

            # Create the actual field
            field = FormBuilder.create_field(
                field_name=field_name,
                metadata=metadata,
                widget=widget,
                render_kw=render_kw_for_field
            )

            attributes[field_name] = field

        return attributes

    @staticmethod
    def create_field(
        field_name: str,
        metadata: Dict[str, Any],
        widget: Optional[Any],
        render_kw: Dict[str, Any],
    ) -> Field:
        """
        Factory method to create a WTForms Field based on metadata about the field
        (e.g. type, required, readonly, primary_key, enum_class, etc.).

        :param field_name: Name of the field.
        :param metadata: A dictionary of metadata about the field, e.g.:
            {
                "type": "string",
                "required": True,
                "readonly": False,
                "primary_key": False,
                "enum_class": SomeEnum,
                ...
            }
        :param widget: An optional custom widget (WTForms).
        :param render_kw: A dictionary of keyword args for rendering in templates
                          (e.g. {"class": "form-control", "placeholder": "Enter name..."}).
        :return: An instance of a WTForms Field.
        """
        field_type = metadata.get("type", "string")
        required = metadata.get("required", False)
        readonly = metadata.get("readonly", False)
        primary_key = metadata.get("primary_key", False)
        enum_class = metadata.get("enum_class", None)
        choices_metadata = metadata.get("choices", None)

        # Decide validators
        validators = [DataRequired()] if required else [ValidatorOptional()]

        # If user hasn't explicitly overridden 'readonly', set it if metadata says so
        if readonly and "readonly" not in render_kw:
            render_kw["readonly"] = True

        # Identify the base field class from our mapping
        field_class = FORM_FIELD_MAPPING.get(field_type, StringField)

        # If it's a primary key, make it a HiddenField and remove required validators
        if primary_key:
            field_class = HiddenField
            validators = []

        # If the field class is a selection type (e.g., enum or radio)
        if field_class in (SelectField, RadioField):
            if enum_class:
                # Build choices from an Enum class
                choices= [("", "")]
                choices += [(e.value, e.name) for e in enum_class]
            elif choices_metadata:
                # Or from a list of tuples or something custom
                choices = choices_metadata
            else:
                choices = []
            return field_class(
                label=field_name.capitalize(),
                choices=choices,
                validators=validators,
                widget=widget,
                render_kw=render_kw,
            )
        else:
            # Fallback for standard fields (string, email, date, etc.)
            return field_class(
                label=field_name.capitalize(),
                validators=validators,
                widget=widget,
                render_kw=render_kw,
            )

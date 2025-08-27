from typing import List, Dict, Any, Optional, Type, Union

from wtforms import Form

from fastpluggy.core.models_tools.shared import ModelToolsShared
from fastpluggy.core.view_builer.components import FieldHandlingView
from fastpluggy.core.widgets.base import AbstractWidget




class FormWidget(AbstractWidget, FieldHandlingView):
    """
    Unified form widget that can be instantiated in one of three modes:
      1. `fields` is a Dict[name -> FieldType], and `model` is None             → we build a manual form from those FieldType objects.
      2. `fields` is a List[str], and `model` is provided                      → we pull those named attributes out of the model metadata and build fields just for them.
      3. `fields` is None (or empty) and `model` is provided (old behavior)      → auto-generate a full form from the model (minus exclude/extras).
    """

    widget_type = "form"
    macro_name = "render_form"
    render_method = "macro"

    template_name = "widgets/input/form.html.j2"
    category = "input"
    description = "Form component with validation and submission handling"
    icon = "wpforms"

    form: Optional[Form] = None

    def __init__(
        self,
        # Either pass a model, or a fields argument, or both:
        model: Optional[Type[Any]] = None,
        # If you only want a subset of the model’s fields, you can pass fields as List[str], e.g. ["title","price"]
        # If you want to override with custom FieldType objects, pass fields as Dict[str, FieldType].
        fields: Optional[Union[List[str], Dict[str, Any]]] = None,

        # Only used if `fields` is falsy.  (Old “exclude everything except model fields.”)
        exclude_fields: Optional[List[str]] = None,
        readonly_fields: Optional[List[str]] = None,
        additional_fields: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,

        # Standard form attributes
        action: str = "",
        method: str = "POST",
        title: Optional[str] = None,
        submit_label: Optional[str] = "Submit",
        # Extra kwargs forwarded to AbstractWidget / FieldHandlingView
        **kwargs
    ):
        # Keep track of form parameters
        self.model = model
        self.exclude_fields = exclude_fields or []
        self.readonly_fields = readonly_fields or []
        self.additional_fields = additional_fields or {}

        # If data is a model instance or dict, extract it to pre-populate
        self.data = (
            ModelToolsShared.extract_model_data(
                data, fields=None, exclude=self.exclude_fields
            )
            if data
            else {}
        )

        # New: accept `fields` as either List[str] or Dict[str, FieldType]
        if isinstance(fields, list):
            # “Subset by name” mode
            self.fields: List[str] | Dict[str, Any] = fields
        elif isinstance(fields, dict):
            # “Custom FieldType dict” mode
            self.fields = fields
        else:
            # None or empty → fallback to model auto-generate
            self.fields = {}

        # Form metadata
        self.action = action
        self.method = method.upper()
        self.title = title
        self.submit_label = submit_label

        # Call parent constructors
        super().__init__(**kwargs)

        # Placeholder for WTForms Form instance
        self.form = None

    def _generate_form_class(self) -> Type[Form]:
        """
        Build a WTForms.Form subclass in one of three ways:
          1) If `self.fields` is a dict: treat it as “name → FieldType” and build a minimal Form class.
          2) If `self.fields` is a list of names AND `self.model` is provided:
             – fetch those names’ metadata from the model, build FieldTypes for them, and turn into WTForms Fields.
          3) If `self.fields` is empty (falsy) AND `self.model` exists:
             – call FormBuilder.generate_form(...) exactly as before.
        """
        # CASE 1: fields is a dict of custom FieldType instances
        if isinstance(self.fields, dict) and self.fields:
            form_fields = {}
            for name, field_factory in self.fields.items():
                # field_factory might be a FieldType subclass or a ready WTForms Field
                if callable(field_factory):
                    form_fields[name] = field_factory()
                else:
                    form_fields[name] = field_factory
            form_name = (self.model.__name__ + "ManualForm") if self.model else "ManualForm"
            return type(form_name, (Form,), form_fields)

        # CASE 2: fields is a list of strings AND model is present
        if isinstance(self.fields, list) and self.fields:
            from fastpluggy.core.view_builder import FormBuilder

            if not self.model:
                raise ValueError("If you pass a list of field names, `model` must also be provided.")
            # 2a) Grab full metadata from the model, then pick only the keys in self.fields
            full_meta = ModelToolsShared.get_model_metadata(
                model=self.model,
                exclude_fields=None,       # we’ll filter manually
                readonly_fields=self.readonly_fields
            )
            missing = [n for n in self.fields if n not in full_meta]
            if missing:
                raise ValueError(f"These field names were not found on {self.model.__name__}: {missing}")
            # Build a minimal dict[name -> FieldType] for those keys
            minimal_fieldtypes: Dict[str, Any] = {}
            for name in self.fields:
                metadata = full_meta[name]
                # Use the same logic your CrudAdmin.configure_fields uses (mapped to FieldType)
                # For simplicity, call FormBuilder.create_field via a mini-helper.
                # Create a one-field FormBuilder “attributes” dictionary
                widget = None
                render_kw = {}
                wtfield = FormBuilder.create_field(
                    field_name=name,
                    metadata=metadata,
                    widget=widget,
                    render_kw=render_kw,
                )
                minimal_fieldtypes[name] = wtfield
            # Add "additional_fields" if given
            if self.additional_fields:
                minimal_fieldtypes.update(self.additional_fields)
            form_name = self.model.__name__ + "SubsetForm"
            return type(form_name, (Form,), minimal_fieldtypes)

        # CASE 3: fields empty AND model provided
        if not self.fields:
            from fastpluggy.core.view_builder import FormBuilder
            if not self.model:
                raise ValueError("Either `fields` (list or dict) or `model` must be provided to build a form.")
            return FormBuilder.generate_form(
                model=self.model,
                exclude_fields=self.exclude_fields,
                additional_fields=self.additional_fields,
                readonly_fields=self.readonly_fields,
            )

        # (Should never get here, but as a fallback…)
        raise ValueError("Invalid combination of `fields` and `model` in FormWidget.")

    def get_form(self, form_data=None) -> Form:
        """
        Instantiate (or re-populate) the WTForms form:
        - bind POST data via `formdata=form_data`
        - set `data=self.data` to prefill from a model instance/dict
        """
        # Normalize exclude_fields in case of wildcard/overrides
        self.exclude_fields = self.process_fields_names(self.exclude_fields or [])

        if self.form is None:
            FormClass = self._generate_form_class()
            self.form = FormClass(formdata=form_data, data=self.data)
        else:
            self.form.process(formdata=form_data, data=self.data)

        return self.form

    def process(self, form_data=None, **kwargs) -> None:
        """
        Called by the rendering pipeline. Ensures:
          1. `self.form` is instantiated before Jinja tries to call `form.` anything.
          2. Any FieldHandlingView logic (like attaching errors) still runs.
        """
        # Update any dynamic exclude_fields
        self.exclude_fields = self.process_fields_names(self.exclude_fields or [])
        # Force instantiation of the WTForms.Form
        self.get_form(form_data)
        super().process(**kwargs)

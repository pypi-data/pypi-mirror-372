"""
Enhanced Table widget with comprehensive data display capabilities.
Fixed to work properly with the new button system.
"""
import inspect
from copy import deepcopy
from typing import List, Dict, Any, Optional, Union, Callable
from urllib.parse import urlencode

from fastapi import Request
from loguru import logger

from fastpluggy.core.models_tools.pydantic import ModelToolsPydantic
from fastpluggy.core.models_tools.shared import ModelToolsShared
from fastpluggy.core.models_tools.sqlalchemy import ModelToolsSQLAlchemy
from fastpluggy.core.view_builer.components import FieldHandlingView
from fastpluggy.core.widgets.base import AbstractWidget
from fastpluggy.core.widgets.mixins import RequestParamsMixin


class TableWidget(AbstractWidget, RequestParamsMixin, FieldHandlingView):
    """Enhanced data table widget with sorting, filtering, and advanced features."""

    widget_type = "table"
    template_name = "widgets/data/table.html.j2"
    macro_name = "render_table"
    render_method = "macro"

    category = "data"
    description = "Advanced data table with sorting, filtering, and customization capabilities"
    icon = "table"

    def __init__(
        self,
        data: List[Dict[str, Any]] = None,
        title: Optional[str] = None,
        fields: Optional[List[str]] = None,
        columns: Optional[List[str]] = None,  # Keep for backward compatibility
        headers: Optional[Dict[str, str]] = None,
        exclude_fields: Optional[List[Union[str, Any]]] = None,
        links: Optional[List[Union["BaseButtonWidget", Dict[str, Any]]]] = None,
        field_callbacks: Optional[Dict[Union[str, Any], Callable[[Any], Any]]] = None,
        request: Optional[Request] = None,
        sortable: bool = True,
        auto_detect_fields: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)

        # Data and basic configuration
        self.data = data or []
        self.title = title
        self.request = request
        self.sortable = sortable
        self.auto_detect_fields = auto_detect_fields

        # Field configuration - support both 'fields' and 'columns' for compatibility
        self.fields = self.process_fields_names(fields or columns or [])
        self.headers = headers or {}
        self.exclude_fields = self.process_fields_names(exclude_fields or [])

        # Advanced features
        self.field_callbacks = self.process_field_callbacks(field_callbacks or {})
        self.links = links or []

        # Processed data attributes
        self.processed_data = []
        self.sortable_headers = []
        self.has_data = False

    def _auto_detect_fields_and_headers(self, model_or_data):
        """
        Auto-detect fields and generate headers dynamically for the table.
        """
        if not model_or_data:
            return [], {}

        # If we have data, try to use the first item as a model reference
        if isinstance(model_or_data, list) and model_or_data:
            sample_item = model_or_data[0]

            # Handle different model types
            if ModelToolsPydantic.is_model_instance(sample_item):
                fields_metadata = ModelToolsShared.get_model_metadata(type(sample_item), self.exclude_fields)
            elif ModelToolsSQLAlchemy.is_sqlalchemy_model_instance(sample_item):
                fields_metadata = ModelToolsShared.get_model_metadata(type(sample_item), self.exclude_fields)
            elif hasattr(sample_item, '__dict__'):
                # For regular objects, get attributes
                fields_metadata = {
                    key: None for key in sample_item.__dict__.keys()
                    if key not in self.exclude_fields
                }
            elif isinstance(sample_item, dict):
                # For dictionaries, get keys
                fields_metadata = {
                    key: None for key in sample_item.keys()
                    if key not in self.exclude_fields
                }
            else:
                return [], {}
        else:
            # Single model passed
            fields_metadata = ModelToolsShared.get_model_metadata(model_or_data, self.exclude_fields)

        # Get field names and generate headers
        detected_fields = list(fields_metadata.keys())
        headers = {
            field: self.headers.get(field, field.replace("_", " ").title())
            for field in detected_fields
        }

        return detected_fields, headers

    def _build_sortable_headers(self) -> List[Dict[str, Any]]:
        """
        Builds sortable headers for the table.
        """
        if not self.sortable or not self.request:
            # Return simple headers without sorting functionality
            return [
                {
                    "label": self.headers.get(field, field.replace("_", " ").title()),
                    "url": None,
                    "sorted": False,
                    "order": None
                }
                for field in self.fields
            ]

        sortable_headers = []

        # Extract sorting parameters from query
        sort_by = self.get_query_param("sort_by", None, str)
        sort_order = self.get_query_param("sort_order", "asc", str)

        existing_params = dict(self.request.query_params) if self.request.query_params else {}

        for field in self.fields:
            header_label = self.headers.get(field, field.replace("_", " ").title())
            is_sorted = field == sort_by
            new_order = "desc" if is_sorted and sort_order == "asc" else "asc"

            # Build query parameters for sorting
            updated_params = existing_params.copy()
            updated_params["sort_by"] = field
            updated_params["sort_order"] = new_order

            # Generate sorting URL
            base_url = self.request.url.path
            url = f"{base_url}?{urlencode(updated_params)}"

            sortable_headers.append({
                'field_name': field,
                "label": header_label,
                "url": url,
                "sorted": is_sorted,
                "order": sort_order if is_sorted else None
            })

        return sortable_headers

    def _preprocess_data(self, data: List[Any]) -> List[Dict[str, Any]]:
        """
        Process data to exclude specified fields, include @property attributes on
        plain Python objects, and normalize format.
        """
        processed_data: List[Dict[str, Any]] = []
        if not data:
            return processed_data

        for item in data:
            try:
                # 1) If it's a Pydantic model instance, use model_dump()
                if ModelToolsPydantic.is_model_instance(item):
                    processed_item = {
                        key: value
                        for key, value in item.model_dump().items()
                        if key not in self.exclude_fields
                    }

                # # 2) If it's a SQLAlchemy model instance, convert it to dict
                # elif ModelToolsSQLAlchemy.is_sqlalchemy_model_instance(item):
                #     processed_item = ModelToolsSQLAlchemy.model_to_dict(
                #         item, exclude_fields=self.exclude_fields
                #     )

                # 3) If it's a plain Python object with __dict__, include its attributes
                #    AND any @property-decorated attributes on its class
                elif hasattr(item, "__dict__"):
                    # Start with the instance's own __dict__ (excluding private or excluded)
                    processed_item = {
                        key: value
                        for key, value in item.__dict__.items()
                        if not key.startswith("_") and key not in self.exclude_fields
                    }

                    # Now find all @property attributes on the class (including inherited)
                    cls = type(item)
                    for name, descriptor in inspect.getmembers(
                            cls, predicate=lambda x: isinstance(x, property)
                    ):
                        # Skip private/dunder or explicitly excluded names
                        if name.startswith("_") or name in self.exclude_fields:
                            continue

                        # Safely attempt to retrieve the property value
                        try:
                            processed_item[name] = getattr(item, name)
                        except Exception:
                            # If the property getter raises, skip it
                            continue

                # 4) If it's already a dict, just copy (excluding excluded keys)
                elif isinstance(item, dict):
                    processed_item = {
                        key: value
                        for key, value in item.items()
                        if key not in self.exclude_fields
                    }

                # 5) Fallback: try to treat it as an iterable to dict, or wrap as value
                else:
                    if hasattr(item, "__iter__") and not isinstance(item, (str, bytes, dict)):
                        try:
                            processed_item = dict(item)
                        except Exception:
                            processed_item = {"value": item}
                    else:
                        processed_item = {"value": item}

                processed_data.append(processed_item)

            except Exception as e:
                logger.warning(f"Error processing data item: {e}")
                continue

        return processed_data

    def _process_fields_and_headers(self):
        """
        Process fields and headers, auto-detecting if necessary.
        """
        if not self.fields and self.auto_detect_fields:
            self.fields, detected_headers = self._auto_detect_fields_and_headers(self.data)
            # Merge with any manually provided headers
            self.headers.update(detected_headers)
        elif self.fields and not self.headers:
            self.fields = self.process_fields_names(self.fields or [])
            self.headers = {
                field: field.replace("_", " ").title()
                for field in self.fields
            }
        elif not self.fields and self.data:
            # Fallback: use first item keys as fields
            first_item = self.processed_data[0] if self.processed_data else {}
            self.fields = [key for key in first_item.keys() if key not in self.exclude_fields]
            self.headers = {
                field: field.replace("_", " ").title()
                for field in self.fields
            }

    def _apply_field_callbacks(self):
        """
        Apply field-specific callback functions to format field values.
        """
        if not self.field_callbacks:
            return

        for item in self.processed_data:
            for field, callback in self.field_callbacks.items():
                if field in item:
                    try:
                        item[field] = callback(item[field])
                    except Exception as e:
                        logger.warning(f"Error applying callback for field '{field}': {e}")
                        # Keep original value on error

    def create_action_buttons_for_item(self, item: Dict[str, Any]) -> 'ButtonListWidget':
        """
        Create a ButtonListWidget for action buttons for a specific table row.
        This replaces the old get_buttons_for_item method.
        """
        from fastpluggy.core.widgets.categories.input.button_list import ButtonListWidget
        from fastpluggy.core.widgets.categories.input.button import BaseButtonWidget, ButtonWidget, AutoLinkWidget, FunctionButtonWidget

        if not self.links:
            return None

        # Convert links to button widgets
        button_widgets = []

        for link in self.links:
            try:
                if isinstance(link, BaseButtonWidget):
                    # Already a button widget - clone it for this specific item
                    link_copy = deepcopy(link)
                    button_widgets.append(link_copy)

                elif isinstance(link, dict):
                    # Dictionary configuration - create ButtonWidget
                    # Handle URL placeholders
                    link_config = dict(link)  # Copy to avoid modifying original

                    if 'url' in link_config:
                        url = link_config['url']
                        # Replace placeholders in URL
                        for key, value in item.items():
                            url = url.replace(f"{{{key}}}", str(value))
                        link_config['url'] = url

                    # Determine button type
                    if 'route_name' in link_config:
                        button = AutoLinkWidget(**link_config)
                    elif 'call' in link_config:
                        button = FunctionButtonWidget(**link_config)
                    else:
                        button = ButtonWidget(**link_config)

                    button_widgets.append(button)

                else:
                    logger.warning(f"Unsupported link type: {type(link)}")
                    continue

            except Exception as e:
                logger.exception(f"Error creating button for item {item}: {e}")
                # Create error button
                error_button = ButtonWidget(
                    url='#',
                    label='Error',
                    css_class='btn btn-sm btn-danger',
                    onclick=f"alert('Error: {str(e).replace(chr(39), chr(92)+chr(39))}'); return false;",
                    disabled=True
                )
                button_widgets.append(error_button)

        if not button_widgets:
            return None

        # Create ButtonListWidget with the buttons
        action_buttons = ButtonListWidget(
            buttons=button_widgets,
            style="list",  # Use spaced buttons for table actions
            layout="horizontal",
            button_size="sm",
            spacing="tight"
        )
        if hasattr(button_widgets, 'request'):
            button_widgets.request = self.request
        action_buttons.process(item=item)

        return action_buttons

    def process(self, **kwargs) -> None:
        """
        Process the widget data and prepare for rendering.
        """
        try:
            # Step 1: Preprocess the raw data
            self.processed_data = self._preprocess_data(self.data)

            # Step 2: Process fields and headers
            self._process_fields_and_headers()

            # Step 3: Build sortable headers
            self.sortable_headers = self._build_sortable_headers()

            # Step 4: Create action buttons for each item BEFORE formatting fields
            if self.links:
                for item in self.processed_data:
                    # Create ButtonListWidget for this item's actions (using raw values)
                    action_buttons = self.create_action_buttons_for_item(item)
                    if action_buttons:
                        forward_kwargs = {k: v for k, v in kwargs.items() if k != "request"}
                        action_buttons.process(item=item, request=self.request, **forward_kwargs)
                        item['_action_buttons'] = action_buttons

                    # Also keep legacy button data for backward compatibility
                    item['_buttons'] = self.create_action_buttons_for_item(item)

            # Step 5: Apply field callbacks (format data for display)
            self._apply_field_callbacks()

            # Step 6: Set data availability flag
            self.has_data = len(self.processed_data) > 0

            # Store additional parameters
            self.params = kwargs

        except Exception as e:
            logger.exception(f"Error processing table widget: {e}")
            self.has_data = False
            self.processed_data = []
            self.error_message = f"Error processing table: {str(e)}"

    @classmethod
    def get_widget_info(cls) -> Dict[str, Any]:
        """
        Extended widget info including configuration options.
        """
        base_info = super().get_widget_info()
        base_info.update({
            'supports_sorting': True,
            'supports_filtering': True,
            'supports_field_callbacks': True,
            'supports_row_actions': True,
            'configuration_options': {
                'data': 'List of dictionaries or model instances',
                'fields': 'List of field names to display',
                'headers': 'Dictionary mapping field names to display headers',
                'exclude_fields': 'List of fields to exclude from display',
                'field_callbacks': 'Dictionary of field formatters',
                'links': 'List of action buttons/links for each row',
                'sortable': 'Enable/disable sorting functionality',
                'auto_detect_fields': 'Automatically detect fields from data',
            }
        })
        return base_info

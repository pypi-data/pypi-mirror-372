# fastpluggy/core/widgets/categories/input/button_widgets.py
"""
Complete button widget system (updated to remove ButtonGroupWidget duplication).
ButtonGroupWidget functionality is now integrated into ButtonListWidget.
"""

import inspect
from abc import abstractmethod
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlencode

from fastpluggy.core.tools import convert_param_type
from fastpluggy.core.tools.fastapi import inspect_fastapi_route
from fastpluggy.core.tools.inspect_tools import is_internal_dependency
from fastpluggy.core.widgets.base import AbstractWidget


class ButtonWidgetMixin:
    """
    A mixin providing common button utilities like condition evaluation, placeholder replacement,
    and parameter processing.
    """

    @staticmethod
    def replace_placeholders(template: str, item: Optional[Dict[str, Any]] = None) -> str:
        """Replace placeholders like <field_name> with actual values from item."""
        if item and "<" in template and ">" in template:
            for key, value in item.items():
                placeholder = f"<{key}>"
                template = template.replace(placeholder, str(value))
        return template

    @staticmethod
    def evaluate_condition(condition: bool | Callable, item: Optional[Dict[str, Any]]) -> bool:
        """Evaluate a condition that can be a boolean or callable."""
        return condition(item) if callable(condition) else condition

    @staticmethod
    def evaluate_label(label: str | Callable, item: Optional[Dict[str, Any]]) -> str:
        """Evaluate a label that can be a string or callable."""
        return label(item) if callable(label) else label

    @staticmethod
    def process_params(params: Dict[str, Any], item: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Process parameters, replacing placeholders with actual values."""
        if params is None:
            return {}

        return {
            key: ButtonWidgetMixin.replace_placeholders(value, item) if isinstance(value, str) else value
            for key, value in params.items()
        }


class BaseButtonWidget(AbstractWidget, ButtonWidgetMixin):
    """
    Base class for all button widgets.
    """

    widget_type = "base_button"
    template_name = "widgets/input/button.html.j2"
    macro_name = "render_button"
    render_method = "macro"

    category = "input"
    description = "Base button widget with common functionality"
    icon = "mouse-pointer"

    def __init__(
            self,
            label: Optional[str | Callable] = None,
            css_class: Optional[str | Callable] = None,
            condition: bool | Callable[[Optional[Dict[str, Any]]], bool] = True,
            onclick: Optional[str] = None,
            method: Optional[str] = None,
            params: Optional[Dict[str, Any]] = None,
            icon: Optional[str] = None,
            disabled: bool = False,
            **kwargs
    ):
        """
        Initialize base button widget.

        Args:
            label: Button text (can be callable for dynamic labels)
            css_class: CSS classes for styling
            condition: Show/hide condition (can be callable)
            onclick: JavaScript onclick handler
            method: HTTP method (get, post, etc.)
            params: Additional parameters
            icon: Font Awesome icon name
            disabled: Whether button is disabled
        """
        super().__init__(**kwargs)
        self.label = label
        self.css_class = css_class or 'btn btn-primary'
        self.condition = condition
        self.condition_raw = condition
        self.onclick = onclick
        self.method = method or "get"
        self.params = params or {}
        self.icon = icon
        self.disabled = disabled

    def common_process(self, item: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Standardized processing shared across all button widgets.
        """
        self.label = self.evaluate_label(self.label, item)
        self.css_class = self.evaluate_label(self.css_class, item)
        self.condition = self.evaluate_condition(self.condition_raw, item)
        self.method = self.method.lower() if self.method else "get"
        self.params = self.process_params(self.params, item)

    @abstractmethod
    def process(self, item: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Abstract method to be implemented by subclasses."""
        pass

    def _resolve_param_value(self, name: str, item: Optional[dict[str, Any]], default: Any) -> Any:
        """Resolve parameter value from various sources."""
        source = getattr(self, 'param_inputs', {}).get(name, None)
        run_as_task = getattr(self, "run_as_task", False)

        # If the input is a placeholder like "<id>", resolve it from the item
        # todo use replace_placeholder ?
        if isinstance(source, str) and source.startswith("<") and source.endswith(">"):
            key = source[1:-1]
            if item and key in item:
                return item[key]
            else:
                return default if run_as_task else self._raise_missing(name, key, item)

        # If the input is a static value, return it
        if source is not None:
            return source

        # Fallback to item direct lookup
        if item and name in item:
            return item[name]

        # Use default if defined
        if default != inspect.Parameter.empty:
            return default

        if not run_as_task:
            self._raise_missing(name, name, item)

    def _raise_missing(self, param_name: str, lookup_key: str, item: Optional[dict[str, Any]]):
        """Raise error for missing required parameters."""
        raise ValueError(
            f"Missing required parameter '{param_name}'. Tried looking for '{lookup_key}' in item, "
            f"got: {list(item.keys()) if item else 'None'}"
        )


class ButtonWidget(BaseButtonWidget):
    """
    Simple button widget with URL navigation.
    """

    widget_type = "button"
    description = "Simple button widget for navigation and actions"

    def __init__(self, url: str, **kwargs):
        """
        Initialize button widget.

        Args:
            url: Target URL (supports placeholders like <field_name>)
        """
        super().__init__(**kwargs)
        self.url = url

    def process(self, item: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Process button data."""
        self.common_process(item, **kwargs)
        self.url = self.replace_placeholders(self.url, item)


class FunctionButtonWidget(BaseButtonWidget):
    """
    Button widget that executes a function via executor endpoint.
    """

    widget_type = "function_button"
    description = "Button widget for executing server functions"
    icon = "cog"

    def __init__(
            self,
            call: Callable,
            param_inputs: Optional[Dict[str, Any]] = None,
            run_as_task: bool = False,
            **kwargs
    ):
        """
        Initialize function button widget.

        Args:
            call: Function to execute
            param_inputs: Parameter input mappings
            run_as_task: Whether to run as background task
        """
        super().__init__(**kwargs)
        self.call = call
        self.label = self.label or call.__name__.replace('_', ' ').capitalize()
        self.method = 'post'
        self.param_inputs = param_inputs or {}
        self.run_as_task = run_as_task

    def process(self, item: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Process function button data."""
        self.common_process(item, **kwargs)

        self.url = f"/execute/{self.call.__qualname__}"
        # Generate the params
        self.params = self._generate_params(item)
        self.params['_module'] = self.call.__module__
        self.params['_function'] = self.call.__name__

    def _generate_params(self, item: Optional[dict[str, Any]]) -> dict[str, Any]:
        """Generate parameters for function execution."""
        sig = inspect.signature(self.call)
        params_dict = {}

        for name, param in sig.parameters.items():
            if is_internal_dependency(param.annotation):
                continue

            value = self._resolve_param_value(name, item, param.default)
            if value is not None:
                params_dict[name] = convert_param_type(param.annotation, value)

        if self.run_as_task:
            params_dict['_run_as_task'] = 'true'

        return params_dict


class AutoLinkWidget(BaseButtonWidget):
    """
    Advanced button widget that generates links dynamically by mapping table columns
    to FastAPI endpoint parameters.

    This widget uses the `inspect_fastapi_route` utility to detect the HTTP method,
    path parameters, and query parameters of a given FastAPI route. It then dynamically
    generates URLs based on the provided `item` data.
    """

    widget_type = "auto_link"
    description = "Auto-linking button that maps data to FastAPI route parameters"
    icon = "link"

    request = None

    def __init__(
            self,
            route_name: str,
            param_inputs: Optional[Dict[str, Any]] = None,
            **kwargs
    ):
        """
        Initialize the AutoLinkWidget.

        Args:
            route_name: The FastAPI endpoint route name (function name)
            param_inputs: Manual parameter input mappings
        """
        super().__init__(**kwargs)

        self.route_name = route_name
        self.param_inputs = param_inputs or {}
        self.label = self.label or route_name.replace('_', ' ').capitalize()
        self.request = None

    def process(self, item: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """
        Generate the link dynamically based on FastAPI route inspection.

        Args:
            item: The data item being processed
            **kwargs: Additional processing arguments (should include 'request')
        """

        try:
            # Detect the route method and parameters using inspect_fastapi_route
            route_metadata = inspect_fastapi_route(
                app=self.request.app,
                route_name=self.route_name
            )

            # Extract relevant data from the route metadata
            method = route_metadata["methods"][0] if route_metadata["methods"] else "get"
            self.method = method.lower()

            path_param_names = route_metadata["path_params"]
            query_param_names = route_metadata["query_params"]
            body_param_names = route_metadata["body_params"]

            # Match parameters from the item data
            matched_params = self._match_params(
                param_names=path_param_names + query_param_names + body_param_names,
                item=item
            )

            # Separate path and query parameters
            path_params = {
                param['name']: matched_params[param['name']]
                for param in route_metadata["path_params"]
                if param['name'] in matched_params
            }
            query_params = {
                param['name']: matched_params[param['name']]
                for param in route_metadata["query_params"]
                if param['name'] in matched_params
            }

            # Generate the URL
            self.url = self._generate_url(path_params, query_params)

            # Process common button data
            self.common_process(item, **kwargs)
            self.params = matched_params
        except Exception as e:
            # Handle errors gracefully
            self.common_process(item, **kwargs)
            self.url = "#"
            self.params = {}
            self.method = 'get'
            self.error = f"Error generating link: {str(e)}"
            self.disabled = True

    def _match_params(self, param_names: List[Dict[str, Any]], item: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Match route parameters to item columns.

        Args:
            param_names: Parameter descriptors from inspect_fastapi_route
            item: Data item from the table

        Returns:
            Dict of matched parameters
        """
        matched_params = {}

        for param in param_names:
            name = param['name']
            param_type = param.get('type')
            default = param.get('default')

            # Skip if it's a file input (UploadFile/File)
            if param_type == 'file':
                continue

            try:
                # Try to resolve the value
                value = self._resolve_param_value(name, item, default=default)

                # If value is found or a default was given, use it
                if value is not None:
                    matched_params[name] = value
                elif default is None:
                    continue  # Skip missing optional param

            except ValueError:
                # If it's a required parameter, we need to handle this
                if default == inspect.Parameter.empty:
                    raise ValueError(
                        f"Missing required parameter '{name}' for route '{self.route_name}'. "
                        f"Available keys in item: {list(item.keys()) if item else 'None'}, "
                        f"and param_inputs: {list(self.param_inputs.keys()) if self.param_inputs else 'None'}."
                    )

        return matched_params

    def _generate_url(self, path_params: Dict[str, Any], query_params: Dict[str, Any]) -> str:
        """
        Generate the URL with query parameters from matched params.

        Args:
            path_params: Path parameters for the URL
            query_params: Query parameters for the URL

        Returns:
            The generated URL
        """
        try:
            # Use url_for to generate the URL
            url = str(self.request.url_for(self.route_name, **path_params))

            if query_params:
                url = f"{url}?{urlencode(query_params)}"

            return url
        except Exception as e:
            raise ValueError(f"Error generating URL for route '{self.route_name}': {str(e)}")


# Convenience functions for creating common button patterns
def create_action_buttons(
        edit_route: str = None,
        delete_route: str = None,
        view_route: str = None,
        custom_buttons: List[BaseButtonWidget] = None,
        style: str = "list"  # New parameter to choose between "list" and "group"
) -> 'ButtonListWidget':
    """
    Create a standard set of action buttons (Edit, Delete, View).

    DEPRECATED: This function is deprecated and will be removed in a future version.
    Use the `create_action_buttons` function from the `fastpluggy_plugin.crud_tools` package instead.

    Args:
        edit_route: Route name for edit action
        delete_route: Route name for delete action
        view_route: Route name for view action
        custom_buttons: Additional custom buttons
        style: "list" for spaced buttons, "group" for connected buttons

    Returns:
        ButtonListWidget with action buttons
    """
    # Import here to avoid circular imports
    from .button_list import ButtonListWidget
    import warnings

    warnings.warn(
        "The create_action_buttons function in fastpluggy.core.widgets.categories.input.button is deprecated. "
        "Use the create_action_buttons function from fastpluggy_plugin.crud_tools instead.",
        DeprecationWarning,
        stacklevel=2
    )

    buttons = []

    if view_route:
        buttons.append(AutoLinkWidget(
            route_name=view_route,
            label="View",
            css_class="btn btn-sm btn-outline-primary",
            icon="eye"
        ))

    if edit_route:
        buttons.append(AutoLinkWidget(
            route_name=edit_route,
            label="Edit",
            css_class="btn btn-sm btn-outline-secondary",
            icon="edit"
        ))

    if delete_route:
        buttons.append(AutoLinkWidget(
            route_name=delete_route,
            label="Delete",
            css_class="btn btn-sm btn-outline-danger",
            icon="trash",
            onclick="return confirm('Are you sure you want to delete this item?')"
        ))

    if custom_buttons:
        buttons.extend(custom_buttons)

    if style == "group":
        return ButtonListWidget.create_button_group(
            buttons=buttons,
            orientation="horizontal",
            size="sm"
        )
    else:
        return ButtonListWidget(
            buttons=buttons,
            layout="horizontal",
            button_size="sm",
            style="list"
        )



# Export all classes and functions
__all__ = [
    'ButtonWidgetMixin',
    'BaseButtonWidget',
    'ButtonWidget',
    'FunctionButtonWidget',
    'AutoLinkWidget',
    'create_action_buttons',
]

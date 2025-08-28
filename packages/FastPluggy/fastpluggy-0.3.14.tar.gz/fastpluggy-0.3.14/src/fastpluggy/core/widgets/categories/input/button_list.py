# fastpluggy/core/widgets/categories/input/button_list.py
"""
Unified ButtonListWidget - Using objects directly with render_widget()
"""
import logging
from typing import Any, Dict, List, Optional, Union

from fastpluggy.core.widgets import RequestParamsMixin
from fastpluggy.core.widgets.base import AbstractWidget
from fastpluggy.core.widgets.categories.input.button import BaseButtonWidget, AutoLinkWidget, FunctionButtonWidget, \
    ButtonWidget, ButtonWidgetMixin


class ButtonListWidget(AbstractWidget, RequestParamsMixin):
    """
    Unified widget for rendering collections of buttons with flexible layouts and styles.
    Replaces both ButtonGroupWidget and the old ButtonListWidget.
    """

    widget_type = "button_list"

    template_name = "widgets/input/button_list.html.j2"
    macro_name = "render_button_list"
    render_method = "macro"

    category = "input"
    description = "Flexible button collection with multiple layout options"
    icon = "list"

    def __init__(
            self,
            buttons: List[Union[BaseButtonWidget, Dict[str, Any], Any]],
            title: Optional[str] = None,
            layout: str = "vertical",  # "vertical", "horizontal", "grid"
            style: str = "list",  # "list" (spaced) or "group" (connected Bootstrap btn-group)
            button_size: str = "md",  # "sm", "md", "lg"
            spacing: str = "normal",  # "tight", "normal", "loose" (for list style)
            show_count: bool = False,  # Show button count in title
            responsive: bool = True,  # Enable responsive behavior
            **kwargs
    ):
        super().__init__(**kwargs)
        self.buttons = buttons
        self.title = title
        self.layout = layout
        self.style = style
        self.button_size = button_size
        self.spacing = spacing
        self.show_count = show_count
        self.responsive = responsive

        # Processed data will be stored here
        self.processed_buttons = []
        self.list_classes = ""
        self.display_title = None

    def process(self, item: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """
        Process all buttons in the collection and prepare for rendering.
        """
        processed_buttons = []

        for button in self.buttons:
            try:
                processed_button = self._process_individual_button(button, item, **kwargs)
                if processed_button:
                    # Check if the button should be shown (condition check)
                    if ButtonWidgetMixin.evaluate_condition(condition=processed_button.condition, item=item):
                        processed_buttons.append(processed_button)
            except Exception as e:
                # Handle button processing errors gracefully
                error_button = self._create_error_button(button, str(e))
                processed_buttons.append(error_button)

        self.buttons = processed_buttons
        self.processed_buttons = processed_buttons
        self.list_classes = self._build_list_classes()
        self.display_title = self._build_display_title()

    def _process_individual_button(
            self,
            button: Union[BaseButtonWidget, Dict[str, Any], Any],
            item: Optional[Dict[str, Any]],
            **kwargs
    ) -> Optional[BaseButtonWidget]:
        """Process an individual button and return the widget object."""

        # Case 1: Already a widget button
        if isinstance(button, BaseButtonWidget):
            return self._process_widget_button(button, item, **kwargs)

        # Case 2: Dictionary configuration
        elif isinstance(button, dict):
            return self._create_button_from_dict(button, item, **kwargs)

        else:
            raise ValueError(f"Unsupported button type: {type(button)}")

    def _process_widget_button(
            self,
            button: BaseButtonWidget,
            item: Optional[Dict[str, Any]],
            **kwargs
    ) -> BaseButtonWidget:
        """Process a widget button object."""

        # Inject request if available and button supports it
        if  hasattr(button, 'request'):
            if 'request' in kwargs :
                button.request = kwargs['request']
            elif self.request:
                button.request = self.request

        # Apply consistent button sizing
        self._apply_button_size(button)

        button.process(item=item, **kwargs)

        return button


    def _apply_button_size(self, button: BaseButtonWidget) -> None:
        """Apply consistent button sizing."""
        if self.button_size != 'md' and hasattr(button, 'css_class'):
            css_class = getattr(button, 'css_class', '')
            if isinstance(css_class, str):
                # Remove existing size classes and add new one
                css_parts = css_class.split()
                # Keep only base button classes, remove size classes
                css_parts = [c for c in css_parts if not c.startswith('btn-') or c in [
                    'btn', 'btn-primary', 'btn-secondary', 'btn-success', 'btn-danger',
                    'btn-warning', 'btn-info', 'btn-light', 'btn-dark',
                    'btn-outline-primary', 'btn-outline-secondary', 'btn-outline-success',
                    'btn-outline-danger', 'btn-outline-warning', 'btn-outline-info',
                    'btn-outline-light', 'btn-outline-dark'
                ]]

                if self.button_size == 'sm':
                    css_parts.append('btn-sm')
                elif self.button_size == 'lg':
                    css_parts.append('btn-lg')

                button.css_class = ' '.join(css_parts)

    def _create_button_from_dict(
            self,
            button_config: Dict[str, Any],
            item: Optional[Dict[str, Any]],
            **kwargs
    ) -> BaseButtonWidget:
        """Create a button widget from dictionary configuration."""

        # Make a copy to avoid modifying the original
        config = dict(button_config)

        # Apply size if not specified
        if 'css_class' in config:
            self._apply_size_to_css_class(config)

        # Determine button type from config
        button_type = config.get('type', 'button')

        # Create appropriate button widget
        if button_type == 'auto_link' or 'route_name' in config:
            button = AutoLinkWidget(**config)
        elif button_type == 'function_button' or 'call' in config:
            button = FunctionButtonWidget(**config)
        else:
            button = ButtonWidget(**config)

        # Process the button
        return self._process_widget_button(button, item, **kwargs)


    def _apply_size_to_css_class(self, button_config: Dict[str, Any]) -> None:
        """Apply button size to CSS class in config."""
        if self.button_size != 'md':
            css_class = button_config.get('css_class', '')
            if 'btn-sm' not in css_class and 'btn-lg' not in css_class:
                button_config['css_class'] = f"{css_class} btn-{self.button_size}".strip()

    def _create_error_button(self, original_button: Any, error_message: str) -> BaseButtonWidget:
        """Create an error button when processing fails."""
        error_button = ButtonWidget(
            url='#',
            label=f"Error: {type(original_button).__name__}",
            css_class=f"btn btn-{self.button_size} btn-danger",
            onclick=f"alert('Button processing error: {error_message.replace(chr(39), chr(92) + chr(39))}'); return false;",
            disabled=True
        )

        # Process the error button to set attributes
        try:
            error_button.process()
        except Exception:
            # If even the error button fails to process, set basic attributes manually
            error_button.label = error_button.label
            error_button.css_class = error_button.css_class
            error_button.url = error_button.url
            error_button.method = 'get'
            error_button.params = {}
            error_button.onclick = error_button.onclick
            error_button.disabled = error_button.disabled
            error_button.widget_id = error_button.widget_id

        return error_button

    def _build_list_classes(self) -> str:
        """Build CSS classes for the button collection layout."""
        if self.style == "group":
            return self._build_group_classes()
        else:
            return self._build_list_classes_internal()

    def _build_group_classes(self) -> str:
        """Build Bootstrap btn-group classes."""
        classes = ["btn-group"]

        if self.layout == "vertical":
            classes.append("btn-group-vertical")

        if self.button_size != "md":
            classes.append(f"btn-group-{self.button_size}")

        return " ".join(classes)

    def _build_list_classes_internal(self) -> str:
        """Build classes for spaced button lists."""
        classes = ["button-list"]

        # Layout classes
        if self.layout == "horizontal":
            classes.append("d-flex flex-wrap")
        elif self.layout == "grid":
            classes.append("d-grid gap-2")
        else:  # vertical
            classes.append(" gap-1")

        # Spacing classes (only for non-group styles)
        spacing_map = {
            "tight": "gap-1",
            "normal": "gap-2",
            "loose": "gap-3"
        }
        if self.spacing in spacing_map and self.layout != "vertical":
            # Replace default gap for horizontal/grid layouts
            classes = [cls for cls in classes if not cls.startswith("gap-")]
            classes.append(spacing_map[self.spacing])

        return " ".join(classes)

    def _build_display_title(self) -> Optional[str]:
        """Build display title with optional button count."""
        if not self.title:
            return None

        if self.show_count:
            count = len(self.processed_buttons)
            return f"{self.title} ({count})"

        return self.title

    # Factory methods for common patterns
    @classmethod
    def create_button_group(
            cls,
            buttons: List[Union[BaseButtonWidget, Dict[str, Any]]],
            orientation: str = "horizontal",
            size: str = "md",
            **kwargs
    ) -> 'ButtonListWidget':
        """Factory method to create Bootstrap button groups (connected buttons)."""
        return cls(
            buttons=buttons,
            style="group",
            layout=orientation,
            button_size=size,
            **kwargs
        )

    # @classmethod
    # def create_action_list(
    #         cls,
    #         item_actions: List[str] = None,
    #         custom_buttons: List[Union[BaseButtonWidget, Dict[str, Any]]] = None,
    #         title: str = "Actions",
    #         **kwargs
    # ) -> 'ButtonListWidget':
    #     """Factory method to create common action button lists."""
    #     buttons = []
    #
    #     # Add standard action buttons
    #     action_mapping = {
    #         'view': {
    #             'label': 'View',
    #             'css_class': 'btn btn-outline-primary',
    #             'icon': 'eye',
    #             'route_name': 'view_item'
    #         },
    #         'edit': {
    #             'label': 'Edit',
    #             'css_class': 'btn btn-outline-secondary',
    #             'icon': 'edit',
    #             'route_name': 'edit_item'
    #         },
    #         'delete': {
    #             'label': 'Delete',
    #             'css_class': 'btn btn-outline-danger',
    #             'icon': 'trash',
    #             'route_name': 'delete_item',
    #             'onclick': "return confirm('Are you sure you want to delete this item?')"
    #         },
    #         'duplicate': {
    #             'label': 'Duplicate',
    #             'css_class': 'btn btn-outline-info',
    #             'icon': 'copy',
    #             'route_name': 'duplicate_item'
    #         }
    #     }
    #
    #     if item_actions:
    #         for action in item_actions:
    #             if action in action_mapping:
    #                 buttons.append(action_mapping[action])
    #
    #     # Add custom buttons
    #     if custom_buttons:
    #         buttons.extend(custom_buttons)
    #
    #     return cls(buttons=buttons, title=title, **kwargs)


# # Convenience functions
# def create_crud_buttons(
#         show_view: bool = True,
#         show_edit: bool = True,
#         show_delete: bool = True,
#         style: str = "list",
#         **kwargs
# ) -> ButtonListWidget:
#     """Create a standard CRUD button collection."""
#     actions = []
#     if show_view:
#         actions.append('view')
#     if show_edit:
#         actions.append('edit')
#     if show_delete:
#         actions.append('delete')
#
#     return ButtonListWidget.create_action_list(
#         item_actions=actions,
#         title="Actions",
#         style=style,
#         layout="horizontal",
#         button_size="sm",
#         **kwargs
#     )


# Export all classes and functions
__all__ = [
    'ButtonListWidget',
  #  'create_crud_buttons',
]
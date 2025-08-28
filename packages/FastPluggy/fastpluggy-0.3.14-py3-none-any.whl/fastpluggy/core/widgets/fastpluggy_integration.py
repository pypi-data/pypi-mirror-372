"""
FastPluggy integration utilities for the widget system.
"""

from typing import List, Type, Dict, Any

from fastpluggy.core.global_registry import GlobalRegistry
from fastpluggy.core.widgets.base import AbstractWidget


class FastPluggyWidgets:
    """FastPluggy widget integration utilities."""


    @staticmethod
    def register_plugin_widgets(plugin_name: str, widget_classes: List[Type[AbstractWidget]]):
        """
        Register plugin widgets with FastPluggy.

        Args:
            plugin_name: Name of the plugin
            widget_classes: List of widget classes to register
        """
        widget_dict = {}

        for widget_class in widget_classes:
            if hasattr(widget_class, 'widget_type'):
                widget_info = AbstractWidget._build_widget_info(
                    widget_class=widget_class,
                    plugin_name=plugin_name
                )
                widget_dict[widget_class.widget_type] = widget_info

        # Use FastPluggy's extend_globals to merge with existing widgets
        GlobalRegistry.extend_globals('available_widgets', widget_dict)

        print(f"✅ Registered {len(widget_dict)} widgets from plugin '{plugin_name}'")
        return widget_dict

    @staticmethod
    def get_widget_registry() -> Dict[str, Dict[str, Any]]:
        """Get all registered widgets from FastPluggy GlobalRegistry."""
        return GlobalRegistry.get_global('available_widgets', {})

    @staticmethod
    def create_widget_factory():
        """Create a factory function for creating widgets by type."""
        def widget_factory(widget_type: str, **kwargs) -> AbstractWidget:
            """Create a widget instance by type."""
            widgets = FastPluggyWidgets.get_widget_registry()
            widget_info = widgets.get(widget_type)

            if not widget_info:
                raise ValueError(f"Unknown widget type: {widget_type}")

            widget_class = widget_info['class']
            return widget_class(**kwargs)

        return widget_factory

    @staticmethod
    def print_registry():
        """
        Debug function to print all registered widgets.
        """
        widgets = FastPluggyWidgets.get_widget_registry()
        print("\n🔧 Registered Widgets:")
        print("-" * 60)

        for widget_type, widget_info in widgets.items():
            category = widget_info.get('category', 'general')
            plugin = widget_info.get('plugin', 'core')
            template = widget_info.get('template_name', widget_info.get('macro_name', 'custom'))
            print(f"  {widget_type:20} | {category:12} | {plugin:10} | {template}")

        print("-" * 60)
        print(f"Total: {len(widgets)} widgets")

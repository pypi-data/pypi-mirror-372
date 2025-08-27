"""
Base widget classes and registry for FastPluggy widget system.
"""
import inspect
import uuid
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Type


from fastpluggy.core.global_registry import GlobalRegistry


class AbstractWidget(ABC):
    """
    Base class for all widgets using clean class-based configuration.
    Auto-registers with GlobalRegistry when defined.
    """

    # Widget identification
    widget_type: str = "unknown"

    # Template configuration (choose one)
    template_name: Optional[str] = None
    macro_name: Optional[str] = None
    render_method: str = "template"  # "template", "macro", or "custom"

    # Widget metadata
    category: str = "general"
    description: str = ""
    icon: str = "cube"

    widget_extra_js_files: list[str] = []
    widget_extra_css_files: list[str] = []
    # use url_for to make serve_module_static

    def __init_subclass__(cls, **kwargs):
        """Auto-register widget classes when they're defined."""
        super().__init_subclass__(**kwargs)

        if hasattr(cls, 'widget_type') and cls.widget_type != 'unknown':
            cls._build_widget_info(widget_class=cls, plugin_name=None)

    @classmethod
    def _build_widget_info(
        cls,
        widget_class: Type["AbstractWidget"],
        plugin_name: str | None = None
    ) -> dict[str, object]:
        """
        Internal helper that:
        - Assembles the widget_info dict for `widget_class`
        - Registers it in GlobalRegistry under 'available_widgets'
        - Returns the dict for further use (e.g. collecting multiple entries).
        """

        # Base info that’s the same in both contexts:
        widget_info: dict[str, object] = {
            "class": widget_class,
            "class_path": f"{widget_class.__module__}.{widget_class.__qualname__}",
            "widget_type": getattr(widget_class, "widget_type", "unknown"),
            "category": getattr(widget_class, "category", "unknown"),
            "template_name": getattr(widget_class, "template_name", None),
            "macro_name": getattr(widget_class, "macro_name", None),
            "render_method": getattr(widget_class, "render_method", "template"),
            "description": getattr(widget_class, "description", ""),
            "icon": getattr(widget_class, "icon", "cube"),
            "plugin": plugin_name
        }

        # Finally, merge into GlobalRegistry.available_widgets
        GlobalRegistry.extend_globals("available_widgets", {widget_info["widget_type"]: widget_info})

        return widget_info

    def __init__(self, **kwargs):
        self.widget_id = kwargs.get('widget_id', self._generate_id())
        self.collapsed = kwargs.get('collapsed', False)
        self.title = kwargs.get('title', '')
        self.title_css_class = kwargs.get('title_css_class', '')
        self.title_icon = kwargs.get('title_icon', '')
        # usefully when component is used into other one like tabbed widget
        self.hide_header = kwargs.get('hide_header', False)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def _generate_id(self) -> str:
        """Generate a unique ID for this widget."""
        return f"{self.widget_type}_{uuid.uuid4().hex[:8]}"

    def render_html(self, request, templates) -> str|None:
        if not self.template_name:
            return None

        context = self.get_context()

        return templates.get_template(self.template_name).render(**context)

    def get_context(self):
        context = {}
        for name in dir(self):
            # Skip any name that starts with “_”
            # (avoid Python internals like __class__, __module__, etc.)
            if name.startswith("_"):
                continue

            # Skip methods or other callables
            try:
                val = getattr(self, name)
            except Exception:
                continue  # if property getter raises, just skip it

            if inspect.ismethod(val) or inspect.isroutine(val) or inspect.isfunction(val):
                continue

            # At this point, name is a “public” attribute or property that returned something.
            context[name] = val
        return context

    @abstractmethod
    def process(self, **kwargs) -> None:
        """Process the widget data and prepare for rendering."""
        pass

    @classmethod
    def get_widget_info(cls) -> Dict[str, Any]:
        """Get metadata about this widget."""
        return {
            'widget_type': cls.widget_type,
            'template_name': cls.template_name,
            'macro_name': cls.macro_name,
            'category': cls.category,
            'description': cls.description,
            'icon': cls.icon,
        }

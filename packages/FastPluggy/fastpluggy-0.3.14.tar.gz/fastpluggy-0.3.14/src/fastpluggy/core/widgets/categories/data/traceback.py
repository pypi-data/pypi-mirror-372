from typing import Optional, Any

from fastpluggy.core.widgets import AbstractWidget


class TracebackWidget(AbstractWidget):
    """
    A custom view that displays traceback messages in a Bootstrap-style alert card.
    """
    widget_type = "traceback"
    template_name = "widgets/data/traceback.html.j2"
    macro_name = "render_traceback"
    render_method = "macro"

    category = "data"
    description = "Displays traceback messages in an alert card"
    icon = "triangle-exclamation"

    def __init__(self, list_traceback: list, **kwargs):
        super().__init__(**kwargs)
        self.list_traceback = list_traceback

    def process(self, item: Optional[Any] = None, **kwargs) -> dict:
        """Process the widget data and prepare for rendering."""
        return {}

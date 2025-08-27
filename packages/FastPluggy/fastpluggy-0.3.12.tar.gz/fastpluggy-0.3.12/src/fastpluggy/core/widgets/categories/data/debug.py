import json
from typing import Any, Optional

from fastpluggy.core.tools.serialize_tools import serialize_value
from fastpluggy.core.widgets import AbstractWidget


# todo: rename to <somthing>Widget
class DebugView(AbstractWidget):
    """
    A component to render JSON data for debugging purposes.
    """
    widget_type = "debug"
    template_name = "widgets/data/debug.html.j2"

    def __init__(self, data: Any, title: Optional[str] = None,  **kwargs):
        """
        Initialize the DebugView component.

        Args:
            data (Any): The data to render as JSON.
            title (Optional[str]): An optional title for the debug view.
            collapsed (bool): Whether the debug view should be collapsed by default.
        """
        self.json_data = None
        self.data = data
        kwargs['title'] = title or "Debug Information"
        super().__init__(**kwargs)

    def process(self, **kwargs) -> None:
        """
        Process the data and prepare it for rendering.
        """
        self.json_data = json.dumps(serialize_value(self.data), indent=4)
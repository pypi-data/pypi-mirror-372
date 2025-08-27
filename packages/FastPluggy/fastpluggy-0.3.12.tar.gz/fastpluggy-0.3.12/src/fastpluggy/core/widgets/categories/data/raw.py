from typing import Optional, Any

from fastpluggy.core.widgets import AbstractWidget


class RawWidget(AbstractWidget):
    """
    A custom view that imports a template and dynamically sets data in its context.
    """
    widget_type = "raw"

    def __init__(self, source: str, **kwargs):
        super().__init__(**kwargs)
        self.source = source

    def process(self, item: Optional[Any] = None, **kwargs) -> dict:
        pass
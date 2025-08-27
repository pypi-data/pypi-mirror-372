from typing import List

from fastpluggy.core.widgets import AbstractWidget


class TabbedWidget(AbstractWidget):
    """
    A component that renders multiple tabs.
    Each tab can contain:
     - A list of child components (like TableView or FormView) in 'subitems'
     OR
     - A plain HTML string in 'content'
    """

    widget_type = "tabbed_view"
    render_method = "macro"
    macro_name = "render_tabbed_view"

    template_name = "widgets/layout/tabbed.html.j2"
    category: str = "layout"

    def __init__(
            self,
            tabs: List,
            collapsed: bool = False,
            **kwargs
    ):
        kwargs['collapsed'] = collapsed
        kwargs['tabs'] = tabs
        super().__init__(**kwargs)
        self.tabs = tabs

    def process(self, request=None, **kwargs) -> None:
        """
        Process each subcomponent in each tab, letting them do their usual logic
        before rendering.
        """
        # If a tab has "subitems", we call .process() on each item
        for tab in self.tabs:
            if hasattr(tab, "hide_header"):
                tab.hide_header = True
            if hasattr(tab, "process"):
                tab.process(request=request, **kwargs)

from typing import List, Dict, Optional, Union

from fastpluggy.core.widgets import AbstractWidget


class TabbedWidget(AbstractWidget):
    """
    A component that renders multiple tabs with Tabler.io styling.
    
    Each tab can contain:
     - A list of child components (like TableView or FormView) in 'subitems'
     OR
     - A plain HTML string in 'content'
     
    Features:
     - Modern Tabler.io styling
     - Support for icons using Tabler icons (ti ti-*)
     - Proper accessibility attributes
     - Smooth transitions between tabs
    """

    widget_type = "tabbed_view"
    render_method = "macro"
    macro_name = "render_tabbed_view"

    template_name = "widgets/layout/tabbed.html.j2"
    category: str = "layout"

    def __init__(
            self,
            tabs: List,
            tab_icons: Optional[Dict[str, str]] = None,
            collapsed: bool = False,
            **kwargs
    ):
        """
        Initialize a tabbed widget with Tabler.io styling.
        
        Args:
            tabs: List of widgets to display as tabs
            tab_icons: Optional dictionary mapping tab titles to icon names (without the 'ti ti-' prefix)
                       Example: {'Overview': 'info-circle', 'Settings': 'settings'}
            collapsed: Whether the widget should be initially collapsed
            **kwargs: Additional arguments to pass to the parent class
        """
        kwargs['collapsed'] = collapsed
        kwargs['tabs'] = tabs
        super().__init__(**kwargs)
        self.tabs = tabs
        self.tab_icons = tab_icons or {}

    def process(self, request=None, **kwargs) -> None:
        """
        Process each subcomponent in each tab, letting them do their usual logic
        before rendering. Also adds icon information to each tab if specified.
        
        Icon priority:
        1. Use existing tab.icon if already set
        2. Use tab.title_icon if available (new property)
        3. Use tab_icons dictionary if tab.title is a key
        """
        # If a tab has "subitems", we call .process() on each item
        for tab in self.tabs:
            # Set icon based on priority:
            # 1. Already has icon property - do nothing
            # 2. Has title_icon property - use it
            # 3. Title is in tab_icons dictionary - use it
            if not hasattr(tab, "icon"):
                if hasattr(tab, "title_icon"):
                    # Use title_icon property if available
                    tab.icon = tab.title_icon
                elif hasattr(tab, "title") and tab.title in self.tab_icons:
                    # Fall back to tab_icons dictionary
                    tab.icon = self.tab_icons[tab.title]
                
            # Hide header if needed
            if hasattr(tab, "hide_header"):
                tab.hide_header = True
                
            # Process the tab
            if hasattr(tab, "process"):
                tab.process(request=request, **kwargs)

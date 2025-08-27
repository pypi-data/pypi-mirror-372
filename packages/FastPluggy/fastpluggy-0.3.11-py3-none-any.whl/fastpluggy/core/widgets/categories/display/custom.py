from typing import Optional, Any

from fastpluggy.core.widgets import AbstractWidget


class CustomTemplateWidget(AbstractWidget):
    """
    A custom view that imports a template and dynamically sets data in its context.
    """
    widget_type = "custom_template"

    def __init__(
            self,
            template_name: str,
            context: dict = None,
            **kwargs,
    ):
        """
        Initialize the CustomTemplateView.

        Args:
            template_name (str): Name of the Jinja2 template to import.
            context (dict, optional): Context data to pass to the template. Defaults to None.
            **kwargs: Additional parameters for customization.
        """
        self.template_name = template_name
        self.context = context or {}
        self.params = kwargs

    def process(self, item: Optional[Any] = None, **kwargs):
        """
        Process the view by updating the context dynamically.

        Args:
            :param item:
            **kwargs: Additional context data to inject.
        """
        # Merge the provided context with any additional parameters
        if item:
            self.context.update({"item": item})
        self.context.update(kwargs)
        for key, value in self.context.items():
            setattr(self, key, value)

    def render_html(self, request, templates) -> str|None:
        if self.template_name:
            return templates.get_template(self.template_name).render(
                **self.context
            )
        return None
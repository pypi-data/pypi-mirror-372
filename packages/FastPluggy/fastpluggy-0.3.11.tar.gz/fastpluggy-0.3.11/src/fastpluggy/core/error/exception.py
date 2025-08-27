import traceback

from fastapi import Request, status
from fastapi.templating import Jinja2Templates
from jinja2 import PackageLoader, Environment


def custom_exception_handler(request: Request, exc: Exception):
    """
    Custom error handler for unhandled exceptions.
    """
    # Get the full traceback as a string
    traceback_str = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    templates = Jinja2Templates(env=Environment(loader=PackageLoader("fastpluggy", "templates")))

    # Render the custom error template with traceback information
    return templates.TemplateResponse("error.html.j2", {
        "request": request,
        "error_message": str(exc),
        "traceback": traceback_str
    }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

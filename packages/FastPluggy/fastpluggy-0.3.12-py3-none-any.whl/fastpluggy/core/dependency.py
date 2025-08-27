from starlette.requests import Request

from fastpluggy.core.base_module_manager import BaseModuleManager
from fastpluggy.core.view_builder import ViewBuilder


def get_module_manager(request: Request) -> BaseModuleManager:
    domain_module_manager = request.app.state.fastpluggy.get_manager()
    return domain_module_manager


def get_fastpluggy(request: Request):
    fastpluggy = request.app.state.fastpluggy
    return fastpluggy


def get_view_builder(request: Request):
    view_builder = ViewBuilder()
    view_builder.templates =request.app.state.jinja_templates
    return view_builder

def get_templates(request: Request):
    return request.app.state.jinja_templates

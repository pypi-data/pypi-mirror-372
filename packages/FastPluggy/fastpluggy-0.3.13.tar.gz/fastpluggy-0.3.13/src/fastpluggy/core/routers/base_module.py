from fastapi import APIRouter, Depends, Request
from loguru import logger
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse

from fastpluggy.core.database import get_db
from fastpluggy.core.dependency import get_fastpluggy, get_view_builder
from fastpluggy.core.flash import FlashMessage
from fastpluggy.core.models_tools.sqlalchemy import ModelToolsSQLAlchemy
from fastpluggy.core.plugin_state import PluginState
from fastpluggy.core.repository.app_settings import update_db_settings
from fastpluggy.core.tools.fastapi import redirect_to_previous, list_router_routes
from fastpluggy.core.tools.serialize_tools import serialize_value
from fastpluggy.core.view_builer.components.model import ModelView
from fastpluggy.core.widgets import TableWidget, FormWidget, FunctionButtonWidget
from fastpluggy.core.widgets.categories.data.debug import DebugView
from fastpluggy.core.widgets.categories.data.traceback import TracebackWidget
from fastpluggy.core.widgets.categories.display.custom import CustomTemplateWidget
from fastpluggy.core.widgets.categories.input.button_list import ButtonListWidget
from fastpluggy.core.widgets.categories.layout.tabbed import TabbedWidget
from fastpluggy.core.widgets.render_field_tools import RenderFieldTools

base_module_router = APIRouter(
    prefix="/base_module",
    tags=["admin"]
)


def get_current_module(
        request: Request,
        module_name: str,
        fast_pluggy
) -> PluginState | None:
    """
    Helper function to retrieve the current module (plugin or domain) from fast_pluggy.
    Adds an error flash message and returns None if not found or unsupported.
    """
    logger.debug(f"Fetching module - module_name: {module_name}")

    manager = fast_pluggy.get_manager()

    current_module = manager.modules.get(module_name)

    if not current_module:
        logger.error(f"Module module_name: {module_name} not found.")
        if request:
            FlashMessage.add(
                request=request,
                message=f"Module '{module_name}' not found",
                category="error"
            )
        return None

    return current_module


@base_module_router.get("/{plugin_name}/overview", response_class=HTMLResponse)
def get_overview_module(
        request: Request,
        plugin_name: str,
        fast_pluggy=Depends(get_fastpluggy),
        view_builder=Depends(get_view_builder),
):
    """
    Displays the overview page for a specific module.
    """
    current_module = get_current_module(module_name=plugin_name, fast_pluggy=fast_pluggy, request=request)
    if not current_module:
        return redirect_to_previous(request)

    models = ModelToolsSQLAlchemy.get_sqlalchemy_models(current_module.package_name)
    # Prepare the data for the TableWidget
    router_data = []
    if current_module.plugin.module_router:
        module_router = current_module.plugin.module_router
        if isinstance(module_router, list):
            # Handle case where module_router is a list of routers
            for router in module_router:
                if router:
                    router_data.extend(list_router_routes(router))
        else:
            # Handle case where module_router is a single router
            router_data = list_router_routes(module_router)

    #    from fastpluggy.core.routers.actions.modules import install_module_requirements
    # from fastpluggy.core.routers.actions.modules import load_domain_module
    #    from fastpluggy.core.routers.actions.modules import update_plugin_from_git
    from fastpluggy.core.routers.actions import reload_fast_pluggy
    from fastpluggy.core.plugin.service import PluginService

    settings_tittle = current_module.plugin.module_settings.__name__ if current_module.plugin.module_settings else "No settings"
    items = []
    if current_module.traceback:
        items.append(TracebackWidget(list_traceback=current_module.traceback, title="Traceback"))
    # Extract plugin data for the custom card
    plugin_data = current_module.to_dict()

    items.extend([
        DebugView(data=plugin_data, title="Module data", collapsed=True),
        ButtonListWidget(buttons=[
            FunctionButtonWidget(
                label="Install Requirements",
                call=PluginService.install_module_requirements,
                css_class="btn btn-secondary",
                param_inputs={'module_name': plugin_name},  # param for url
                condition=current_module.plugin.requirements_exists is True,
            ),
            FunctionButtonWidget(
                call=PluginService.remove_plugin,
                label='<i class="fa-solid fa-trash"></i> Delete',
                css_class="btn btn-danger",
                onclick="return confirm('Are you sure you want to delete this plugin?');",
                param_inputs={'plugin_name': plugin_name}  # param mapping for item
            ),
            FunctionButtonWidget(call=reload_fast_pluggy, label="Reload FastPluggy"),
            # todo: fix that to use abstract manager
            # FunctionButtonWidget(
            #    call=update_plugin_from_git,
            #    label="Update Plugin",
            #    css_class="btn btn-secondary",
            #    param_inputs={
            #        'module_name': plugin_name,
            #    },
            # ),
        ]),
        CustomTemplateWidget(
            template_name="admin/module_overview.html.j2",
            context={'plugin_data': plugin_data}
        ),
        TabbedWidget(
            tabs=[
                TableWidget(
                    title="Available Models",
                    title_icon="fa fa-database",
                    data=serialize_value(models),
                    links=[
                        # LinkHelper.get_crud_link('<class_name>', "create"),
                    ]
                ),
                TableWidget(
                    title="Available Routes",
                    title_icon="fa fa-route",
                    data=router_data,
                    fields=['name', 'path', 'methods', 'path_params', 'query_params', 'body_params'],
                    field_callbacks={
                        'methods': RenderFieldTools.render_http_verb_badges,
                    }
                ),
                ModelView(
                    title=f'Settings : {settings_tittle}',
                    title_icon="fa fa-gear",
                    model=current_module.settings
                )
            ]
        ),
    ])

    return view_builder.generate(
        request,
        title=f"{current_module.module_type.capitalize()} {current_module.plugin.module_name} overview",
        widgets=items
    )


@base_module_router.get("/{plugin_name}/settings", response_class=HTMLResponse)
def get_plugin_settings(
        request: Request,
        plugin_name: str,
        fast_pluggy=Depends(get_fastpluggy),
        view_builder=Depends(get_view_builder),
):
    """
    Displays the settings page for a specific module.
    """
    current_module = get_current_module(request, plugin_name, fast_pluggy)
    if not current_module:
        return redirect_to_previous(request)

    settings = current_module.settings
    items = []

    if settings:
        items.append(FormWidget(
            model=settings,
            data=settings,
            readonly_fields=['namespace']
        ))

    return view_builder.generate(
        request,
        title=f"{current_module.module_type.capitalize()} {current_module.plugin.module_name} settings",
        widgets=items
    )


@base_module_router.post("/{plugin_name}/settings")
async def save_plugin_settings(
        request: Request,
        plugin_name: str,
        db: Session = Depends(get_db),
        fast_pluggy=Depends(get_fastpluggy),
):
    """
    Saves the updated settings for a specific module.
    """
    current_module = get_current_module(request, plugin_name, fast_pluggy)
    if not current_module:
        return redirect_to_previous(request)

    current_settings = current_module.settings
    form_data = await request.form()
    new_params = dict(form_data)

    update_db_settings(current_settings, db, new_params)

    # Reload application to apply new settings if necessary
    fast_pluggy.load_app()
    FlashMessage.add(request=request, message=f"Settings of '{plugin_name}' updated!", category="success")
    return redirect_to_previous(request)

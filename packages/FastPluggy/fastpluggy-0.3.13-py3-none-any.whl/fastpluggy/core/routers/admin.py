from typing import Optional

import httpx
from fastapi import APIRouter, Depends, Request, Form
from fastapi import UploadFile, File
from loguru import logger
from starlette import status
from starlette.responses import RedirectResponse

from fastpluggy.core.base_module_manager import BaseModuleManager
from fastpluggy.core.config import FastPluggyConfig
from fastpluggy.core.dependency import get_view_builder, get_fastpluggy, get_module_manager
from fastpluggy.core.flash import FlashMessage
from fastpluggy.core.menu.decorator import menu_entry
from fastpluggy.core.tools.fastapi import redirect_to_previous
from fastpluggy.core.widgets import TableWidget
from fastpluggy.core.widgets.categories.data.debug import DebugView
from fastpluggy.core.widgets.categories.display.custom import CustomTemplateWidget
from fastpluggy.core.widgets.categories.input.button import AutoLinkWidget, FunctionButtonWidget
from fastpluggy.core.widgets.categories.input.button_list import ButtonListWidget
from fastpluggy.core.widgets.render_field_tools import RenderFieldTools

admin_router = APIRouter(
    tags=["admin"]
)


@menu_entry(label="Manage Plugins", icon="fa-solid fa-screwdriver-wrench", type='admin', position=1, divider_after=True)
@admin_router.get("/plugins", name="list_plugins")
def list_plugins(
        request: Request, plugin_manager: BaseModuleManager = Depends(get_module_manager),
        view_builder=Depends(get_view_builder),
        fast_pluggy=Depends(get_fastpluggy)
):
    from fastpluggy.core.routers.actions import reload_fast_pluggy
    from fastpluggy.core.routers.actions.modules import toggle_module_status
    from fastpluggy.core.tools.system import restart_application
    from fastpluggy.core.tools.system import restart_application_force
    buttons = [
        AutoLinkWidget(
            label='<i class="fa fa-gear me-1"></i>App Settings', route_name='app_settings',
        ),
        FunctionButtonWidget(call=reload_fast_pluggy, label="Reload FastPluggy"),
        FunctionButtonWidget(
            call=restart_application,
            label="Restart App (SIGINT)",
        ),
        FunctionButtonWidget(
            call=restart_application_force,
            label="Restart App (SIGKILL)",
        ),
    ]

    # if plugin_manager.is_module_loaded('tasks_worker'):
    #     try:
    #         from fastpluggy_plugin.tasks_worker.tasks.plugin_update import check_for_plugin_updates
    #         buttons.append(
    #             FunctionButtonView(label="Check plugin update", call=check_for_plugin_updates, run_as_task=True)
    #         )
    #     except Exception:
    #         logger.exception("No plugins task_worker")

    data = [item.to_dict() for item in plugin_manager.modules.values()]
    data.sort(key=lambda x: x.get("name", ""))

    data_raw = [{key: item.to_dict()} for key, item in plugin_manager.modules.items()]

    items = [
        ButtonListWidget(
            title='Actions',
            buttons=buttons,
        ),
        TableWidget(
            title='Plugin List',
            fields=["module_menu_icon", 'have_update', 'module_name', 'module_type', 'version_html', 'status_html'],
            data=data,
            field_callbacks={
                'have_update': lambda value: '<i class="fa-solid fa-arrow-up me-1"></i>' if value else '',
                'module_menu_icon': RenderFieldTools.render_icon,
                'module_name': lambda value: f'<a href="{request.url_for("get_overview_module", plugin_name=value)}">{value}</a>',
            },
            headers={
                'module_menu_icon': 'icon',
                'module_type': 'type',
                'version_html': 'version',
                'status_html': 'status',
            },
            links=[
                FunctionButtonWidget(
                    call=toggle_module_status,
                    label=lambda item: "Disable" if item["enabled"] else "Enable",
                    css_class=lambda item: "btn btn-warning" if item["enabled"] else "btn btn-success",
                    param_inputs={
                        "plugin_name": "<module_name>",  # map function param to item["name"]
                    },
                ),
                AutoLinkWidget(
                    label='<i class="fa-solid fa-magnifying-glass me-1"></i> View',
                    route_name='get_overview_module',
                    css_class="btn btn-info",
                    param_inputs={'plugin_name': '<module_name>'}  # param mapping for item
                ),
                AutoLinkWidget(
                    label='<i class="fa-solid fa-gear"></i> Configure',
                    route_name='get_plugin_settings',
                    css_class=lambda item: "btn btn-info disabled" if item['settings'] is None else "btn btn-info",
                    param_inputs={'plugin_name': '<module_name>'}
                ),
                # todo: inject this from git_module_manager
                #FunctionButtonWidget(
                #    call=update_plugin_from_git,
                #    label="Update Plugin",
                #    css_class="btn btn-secondary",
                #    condition=lambda task: task['git_available'] is True),
            ]
        ),
        DebugView(data=data_raw, title="Plugin data", collapsed=True),
    ]
    from fastpluggy.core.view_builder.builder import inject_widgets
    inject_widgets(items, tag='admin_plugins_list_more')
    # todo make a widget for this
    #settings = FastPluggyConfig()
    # if settings.fp_install_enabled:
    #     items.append(CustomTemplateWidget(
    #         template_name="admin/install_module.html.j2",
    #         context={
    #             "default_plugin_url": fast_pluggy.settings.plugin_list_url,
    #             "fetch_plugin_url": request.url_for('fetch_plugins'),
    #             "install_plugin_url": request.url_for('install_plugin'),
    #             "install_enabled":  settings.fp_install_enabled,
    #         }
    #     ))
    return view_builder.generate(
        request,
        title="Plugin Administration",
        widgets=items
    )


@admin_router.post("/install")
async def install_plugin(
        request: Request,
        file: Optional[UploadFile] = File(None),
        git_url: Optional[str] = Form(None),
        plugin_name: Optional[str] = Form(None),
        plugin_manager: BaseModuleManager = Depends(get_module_manager),
):
    """
    Route for installing a new plugin (upload ZIP file or install from Git)
    """
    settings = FastPluggyConfig()
    # Check if installation is enabled in the configuration
    if not settings.fp_install_enabled:
        FlashMessage.add(request, "Plugin installation is disabled by configuration.", category="error")
        return RedirectResponse(url=request.url_for("list_plugins"), status_code=status.HTTP_303_SEE_OTHER)

    installer = PluginInstaller(plugin_manager)
    url_redirect = request.url_for("list_plugins")
    if file:
        result = installer.extract_and_install_zip(file)
    elif git_url:
        if plugin_name is None:
            plugin_name = git_url.rsplit('/')[-1].split('.')[0]
        result = installer.install_from_git(git_url=git_url, plugin_name=plugin_name)
    else:
        FlashMessage.add(request, "You must provide either a plugin file or a git URL.", category="error")
        return RedirectResponse(url=url_redirect, status_code=status.HTTP_303_SEE_OTHER)

    FlashMessage.add(request, result["message"], category="success" if result["status"] == "success" else "error")
    return RedirectResponse(url=url_redirect, status_code=status.HTTP_303_SEE_OTHER)


@admin_router.post("/plugin/fetch", name="fetch_plugins")
async def fetch_plugins(
        request: Request,
        url: str = Form(...),  # URL to fetch plugins from
        plugin_manager: BaseModuleManager = Depends(get_module_manager),
        view_builder=Depends(get_view_builder),
):
    """
    Fetches a list of plugins from a remote URL.

    :param plugin_manager:
    :param view_builder:
    :param request: FastAPI request object.
    :param url: The URL to fetch plugins from.
    """
    # Check if installation is enabled in the configuration
    settings = FastPluggyConfig()
    install_enabled= settings.fp_install_enabled
    try:
        # Fetch plugin list from the given URL
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            plugin_list = response.json()  # Assuming JSON response

        FlashMessage.add(request=request, message="Plugin list fetched successfully", category="success")
    except Exception as e:
        logger.error(f"Failed to fetch plugins: {e}")
        FlashMessage.add(request=request, message="Failed to fetch plugins", category="error")
        return redirect_to_previous(request)

    already_installed = plugin_manager.modules.keys()
    clean_data = []
    for item in plugin_list:
        item['installed'] = bool(item['name'] in already_installed)
        clean_data.append(item)

    # Define links based on installation being enabled
    links = []
    if install_enabled:
        links.append(
            AutoLinkWidget(
                route_name='install_plugin', label="Install Plugin",
                param_inputs={'plugin_name': '<name>', 'git_url': '<git_url>'},
            )
        )

    items = [
        TableWidget(
            data=clean_data,
            fields=['name', 'installed', 'version', 'description'],
            field_callbacks={'installed': RenderFieldTools.render_boolean},
            links=links
        ),
        ButtonListWidget(
            buttons=[
                AutoLinkWidget(label="Back to Plugins", route_name="list_plugins")
            ]
        )
    ]

    # Add a warning message if installation is disabled
    if not install_enabled:
        items.insert(0, CustomTemplateWidget(
            template_name="admin/install_disabled_warning.html.j2",
            context={}
        ) if "install_disabled_warning.html.j2" in request.app.state.jinja_templates.list_templates() else
        CustomTemplateWidget(
            html="""
            <div class="card mb-3">
                <div class="card-body">
                    <div class="alert alert-warning">
                        <h4 class="alert-title">Plugin installation is disabled</h4>
                        <div class="text-muted">Plugin installation has been disabled by the system administrator. You can view available plugins but cannot install them.</div>
                    </div>
                </div>
            </div>
            """
        ))

    return view_builder.generate(
        request,
        title='Available Plugins',
        widgets=items
    )

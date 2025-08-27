from typing import Annotated

from fastpluggy.core.flash import FlashMessage
from fastpluggy.core.plugin.service import PluginService
from fastpluggy.core.tools.inspect_tools import InjectDependency
from fastpluggy.fastpluggy import FastPluggy


def toggle_module_status(plugin_name: str, fast_pluggy: Annotated[FastPluggy, InjectDependency]):
    plugin_manager = fast_pluggy.get_manager()

    current_status = plugin_manager.plugin_states.get(plugin_name, None)
    if current_status is None:
        return FlashMessage(message=f"Plugin '{plugin_name}' not found", category="error")
    if current_status:
        return PluginService.disable_plugin(plugin_name, fast_pluggy=fast_pluggy)
    else:
        return PluginService.enable_plugin(plugin_name, fast_pluggy=fast_pluggy)


# def update_plugin_from_git(
#         module_name: str,
#         fast_pluggy: Annotated[FastPluggy, InjectDependency],
#         update_method: str = 'discard',  # Default method is 'none'
# ):
#     """
#     Updates a plugin from its Git repository. Allows the user to choose between 'stash' and 'discard' methods.
#
#     :param fast_pluggy:
#     :param module_name: The name of the plugin to update.
#     :param update_method: The method to handle local changes (either 'none', 'stash' or 'discard').
#
#     :return: FlashMessage
#     """
#     return_messages = []
#     plugin_manager = fast_pluggy.get_manager()
#     current_module = plugin_manager.modules.get(module_name)
#     if current_module.git_available:
#         installer = PluginInstaller(plugin_manager)
#
#         result = installer.update_from_git(module_name, update_method)
#
#         if result["status"] == "success" and "version" in result:
#             plugin_manager.fast_pluggy.load_app()
#
#         return_messages.append(
#             FlashMessage(result["message"], category="success" if result["status"] == "success" else "error"))
#     else:
#         return_messages.append(
#             FlashMessage(message=f"Plugin '{module_name}' is not available from Git", category="error"))
#
#     return_messages.append(
#         RedirectResponse(url=fast_pluggy.settings.fp_admin_base_url, status_code=status.HTTP_303_SEE_OTHER)
#     )
#     return return_messages

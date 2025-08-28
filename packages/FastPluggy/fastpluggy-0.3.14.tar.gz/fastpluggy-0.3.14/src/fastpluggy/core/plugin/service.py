import shutil
import sys
from typing import Annotated

from loguru import logger
from starlette import status
from starlette.responses import RedirectResponse

from fastpluggy.core.database import session_scope
from fastpluggy.core.flash import FlashMessage
from fastpluggy.core.plugin import repository
from fastpluggy.core.tools.inspect_tools import InjectDependency


class PluginService:

    @staticmethod
    def enable_plugin(plugin_name: str, fast_pluggy: "FastPluggy"):
        """
        Enables a plugin and refreshes the plugins.
        """
        try:
            with session_scope() as db_session:
                # 1) persist status change
                repository.update_plugin_status(db=db_session, plugin_name=plugin_name, status=True)

            # 2) do any side effects (reload, events, flash)
            fast_pluggy.load_app()

            logger.info(f"Plugin '{plugin_name}' enabled.")
            return FlashMessage(message=f"Plugin '{plugin_name}' enabled.", category='success')

        except Exception as e:
            logger.error(f"Error enabling plugin '{plugin_name}': {e}")
            return FlashMessage(message=f"Error enabling plugin '{plugin_name}': {e}", category='error')

    @staticmethod
    def disable_plugin(plugin_name: str, fast_pluggy: "FastPluggy"):
        """
        Disable a plugin and refreshes the plugins.
        """
        try:
            with session_scope() as db_session:
                # 1) persist status change
                repository.update_plugin_status(db=db_session, plugin_name=plugin_name, status=False)

            # 2) do any side effects (reload, events, flash)
            fast_pluggy.load_app()

            logger.info(f"Plugin '{plugin_name}' disabled.")
            return FlashMessage(message=f"Plugin '{plugin_name}' disabled.", category='success')

        except Exception as e:
            logger.error(f"Error disabling plugin '{plugin_name}': {e}")
            return FlashMessage(message=f"Error disabling plugin '{plugin_name}': {e}", category='error')

    @staticmethod
    def install_module_requirements(
            module_name: str,
            fast_pluggy: Annotated["FastPluggy", InjectDependency]
    ):
        """
        Installs the requirements for a specific module.
        """
        logger.debug(f"Installing requirements -  module_name: {module_name}")
        manager = fast_pluggy.get_manager()
        current_module = manager.modules.get(module_name)
        if not current_module:
            return FlashMessage(message=f"Plugin '{module_name}' not found", category="error")

        if current_module.plugin.requirements_exists:
            from fastpluggy.core.tools.install import install_requirements
            success = install_requirements(requirements_file=str(current_module.plugin.requirements_path))
            current_module.requirements_installed = success
            logger.info(f"Installed requirements for module '{current_module.plugin.module_name}'.")

            if success:
                return FlashMessage(
                    f"Requirements for {current_module.module_type} '{module_name}' installed successfully!", "success")
            else:
                return FlashMessage(f"Failed to install requirements for {current_module.module_type} '{module_name}'.",
                                    "error")
        else:
            return FlashMessage(f"No requirements found for {current_module.module_type} '{module_name}'.", "info")


    @staticmethod
    def remove_plugin(plugin_name: str, fast_pluggy: Annotated["FastPluggy", InjectDependency]):
        manager = fast_pluggy.get_manager()

        try:
            # Check if the plugin exists
            if not manager.module_directory_exists(plugin_name):
                logger.error(f"Plugin '{plugin_name}' not found for removal.")
                raise FileNotFoundError(f"Plugin '{plugin_name}' not found.")

            # Disable the plugin before removal
            PluginService.disable_plugin(plugin_name=plugin_name, fast_pluggy=fast_pluggy)

            # Get plugin path
            module_info = manager.modules.get(plugin_name)
            plugin_path = module_info.path

            # Remove plugin directory
            shutil.rmtree(plugin_path)
            logger.info(f"Plugin directory '{plugin_path}' removed.")

            # Clean sys.modules
            if plugin_name in sys.modules:
                del sys.modules[plugin_name]
                logger.info(f"Module '{plugin_name}' removed from sys.modules.")

            # Reload plugins
            fast_pluggy.load_app()

            return [
                FlashMessage(message=f"Plugin '{plugin_name}' removed successfully", category="success"),
                RedirectResponse(
                    url=fast_pluggy.settings.fp_admin_base_url+'/plugins',
                    status_code=status.HTTP_303_SEE_OTHER
                )
            ]

        except FileNotFoundError:
            return FlashMessage(message=f"Plugin '{plugin_name}' not found", category="error")

        except Exception as e:
            logger.error(f"Error removing plugin '{plugin_name}': {e}")
            return FlashMessage(message=f"Error removing plugin: {str(e)}", category="error")

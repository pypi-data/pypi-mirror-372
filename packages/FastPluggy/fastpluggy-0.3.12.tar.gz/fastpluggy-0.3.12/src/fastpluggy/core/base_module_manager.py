import inspect
import logging
import traceback
import types
from abc import ABC
from importlib.metadata import entry_points
from pathlib import Path
from typing import Dict, Any, List

import sys
from fastapi import FastAPI
from jinja2 import FileSystemLoader
from loguru import logger

from fastpluggy.core.database import session_scope
from fastpluggy.core.module_base import FastPluggyBaseModule
from fastpluggy.core.plugin.dependency_resolver import PluginDependencyResolver
from fastpluggy.core.plugin.repository import get_all_modules_status
from fastpluggy.core.plugin.service import PluginService
from fastpluggy.core.plugin_state import PluginState
from fastpluggy.core.tools.fs_tools import is_python_module
from fastpluggy.core.tools.inspect_tools import get_module, call_with_injection, find_package_source_from_pyproject


class BaseModuleManager(ABC):
    def __init__(self, app: FastAPI, fast_pluggy):
        self.app = app
        self.fast_pluggy = fast_pluggy

        self.modules: Dict[str, PluginState] = {}

        self.template_loaders: Dict[str, FileSystemLoader] = {}

        # self.db_session: Session = next(get_db())
        self.plugin_states: Dict[str, bool] = {}

        self.refresh_plugins_states()

    def refresh_plugins_states(self):
        with session_scope() as db_session:
            self.plugin_states = get_all_modules_status(db=db_session)

    def get_template_loaders(self):
        template_loaders = {}
        for item_info in self.modules.values():
            if self.is_module_loaded(item_info) and item_info.plugin.templates_dir:
                name = item_info.plugin.module_name
                template_loader = FileSystemLoader(str(item_info.plugin.templates_dir))
                template_loaders[name] = template_loader
                logger.info(f"Added templates for module '{name}' from {item_info.plugin.templates_dir}")

        return template_loaders

    def register_all_routes(self):
        for name, item_info in self.modules.items():
            if self.is_module_loaded(item_info):
                self.include_routes(item_info)

    def include_routes(self, module_info: PluginState):
        module_router = module_info.plugin.module_router
        if isinstance(module_router, types.FunctionType):
            try:
                module_info.plugin.module_router = module_info.plugin.module_router()
                logger.debug(f"📡 Router resolved for plugin '{module_info.plugin.module_name}'")
            except Exception as e:
                module_info.plugin.module_router = None
                module_info.error.append(f"Router loading failed: {e}")
                module_info.traceback.append(traceback.format_exc())
                logger.warning(f"⚠️ Could not resolve module_router for '{module_info.plugin.module_name}': {e}")
            module_router = module_info.plugin.module_router

        # Handle case where module_router is a list of routers
        if isinstance(module_router, list):
            for router in module_router:
                if router:
                    try:
                        url = f"/{module_info.module_type}/{module_info.plugin.module_name}" if module_info.plugin.module_mount_url is None else module_info.plugin.module_mount_url

                        if len(router.tags) == 0:
                            router.tags.append(module_info.plugin.module_name)

                        # Patch operation_id to avoid duplicates in OpenAPI
                        for route in router.routes:
                            if hasattr(route, "operation_id") and route.operation_id:
                                continue
                            if hasattr(route, "name") and route.name:
                                safe_module = module_info.plugin.module_name.replace(".",
                                                                                     "_") if module_info.plugin.module_name else "unknown"
                                route.operation_id = f"{safe_module}_{route.name}"

                        self.fast_pluggy.app.include_router(
                            router, prefix=url,
                            tags=router.tags,
                            include_in_schema=self.fast_pluggy.settings.include_in_schema_fp
                        )

                        logger.info(
                            f"Router for module '{module_info.plugin.module_name}' included with prefix '{url}'")
                    except Exception as err:
                        logger.exception(f"Error including router for module '{module_info.plugin.module_name}': {err}")
                        module_info.error.append(f"Router {router} loading failed: {err}")


        # Handle case where module_router is a single router
        elif module_router:
            url = f"/{module_info.module_type}/{module_info.plugin.module_name}" if module_info.plugin.module_mount_url is None else module_info.plugin.module_mount_url

            if len(module_router.tags) == 0:
                module_router.tags.append(module_info.plugin.module_name)

            # Patch operation_id to avoid duplicates in OpenAPI
            for route in module_router.routes:
                if hasattr(route, "operation_id") and route.operation_id:
                    continue
                if hasattr(route, "name") and route.name:
                    safe_module = module_info.plugin.module_name.replace(".", "_") if module_info.plugin.module_name else "unknown"
                    route.operation_id = f"{safe_module}_{route.name}"

            self.fast_pluggy.app.include_router(
                module_router, prefix=url,
                tags=module_router.tags,
                include_in_schema=self.fast_pluggy.settings.include_in_schema_fp
            )

            logger.info(f"Router for module '{module_info.plugin.module_name}' included with prefix '{url}'")

    def is_module_loaded(self, module_or_name):
        """
        Checks if a module exists and is loaded correctly.
        Accepts either the module name or a PluginState instance.

        :param module_or_name: PluginState object or module name string.
        :return: True if the module is enabled and loaded, False otherwise.
        """
        if isinstance(module_or_name, str):
            module_info = self.modules.get(module_or_name)
        else:
            module_info = module_or_name

        return (
                module_info is not None
                and isinstance(module_info, PluginState)
                and module_info.plugin is not None
                and module_info.enabled
                and module_info.loaded
        )

    def module_directory_exists(self, plugin_name: str) -> bool:
        """
        Checks if a plugin exists in the plugin directory.
        """
        module_info = self.modules.get(plugin_name)
        plugin_path = module_info.path

        exists = plugin_path.is_dir() and any(plugin_path.glob("*.py"))
        if exists:
            logger.info(f"Plugin '{plugin_name}' exists.")
        else:
            logger.warning(f"Plugin '{plugin_name}' does not exist.")
        return exists

    def _get_extra_files(self, attribute) -> List[Any]:
        files = []
        for name, module_info in self.modules.items():
            if not module_info.loaded:
                continue

            plugin_attr = getattr(module_info.plugin, attribute, None)
            if plugin_attr:
                # plugin_attr is expected to be a list of paths
                files.extend(plugin_attr)

        return list(dict.fromkeys(files))

    def get_extra_js_files(self):
        return self._get_extra_files("extra_js_files")

    def get_extra_css_files(self):
        return self._get_extra_files("extra_css_files")

    def discover_plugins(self, folder: str, module_type: str):
        folder_path = Path(folder)

        if folder_path.exists():
            # Add folder to module search path
            domain_path = folder_path.resolve()
            sys.path.append(str(domain_path))

            logger.info(f"🔍 Discovering {module_type} modules in {domain_path}")

            for plugin_dir in folder_path.iterdir():
                if not plugin_dir.is_dir() or plugin_dir.name.startswith('.'):
                    continue

                # Check if it's a Python module or has a pyproject.toml file
                has_pyproject = (plugin_dir / "pyproject.toml").exists()
                if not is_python_module(plugin_dir) and not has_pyproject:
                    logger.debug(f"Skipping {plugin_dir.name}: not a Python module and no pyproject.toml found")
                    continue

                plugin_file = plugin_dir / "plugin.py"
                plugin_dir_name = plugin_dir.name

                plugin_state = PluginState(
                    module_type=module_type,
                    path=plugin_dir,
                )
                logging.info(f"plugin file : {plugin_file}")

                # Initialize pyproject_package_name to None
                pyproject_package_name = None

                # Check for pyproject.toml if plugin.py doesn't exist
                if not plugin_file.exists():
                    # Try to find package source from pyproject.toml
                    init_path, pyproject_package_name = find_package_source_from_pyproject(plugin_dir)
                    if init_path and init_path.exists():
                        # If we found a valid init_path from pyproject.toml, update plugin_dir
                        logger.info(f"Found package source directory from pyproject.toml for {plugin_dir_name}")
                        plugin_dir = init_path.parent
                        plugin_file = plugin_dir / "plugin.py"
                        # Update plugin_state.path to match the new plugin_dir
                        plugin_state.path = plugin_dir

                        # Check if plugin.py exists in the new directory
                        if not plugin_file.exists():
                            msg = f"Missing plugin.py in {plugin_dir_name} (even after finding source dir from pyproject.toml)"
                            logger.warning(f"❌ {msg}")
                            plugin_state.error.append(msg)
                            plugin_state.plugin = FastPluggyBaseModule(module_name=plugin_dir_name)
                            self.modules[plugin_dir_name] = plugin_state
                            continue
                    else:
                        # If we couldn't find a valid init_path from pyproject.toml, continue with the error
                        msg = f"Missing plugin.py in {plugin_dir_name}"
                        logger.warning(f"❌ {msg}")
                        plugin_state.error.append(msg)
                        plugin_state.plugin = FastPluggyBaseModule(module_name=plugin_dir_name)
                        self.modules[plugin_dir_name] = plugin_state
                        continue

                try:
                    # STEP 1: Import module
                    # Use package_name from pyproject.toml if available, otherwise use plugin_dir_name
                    module_name_to_import = pyproject_package_name if pyproject_package_name else plugin_dir_name
                    logger.info(f"Importing module {module_name_to_import} from {plugin_dir.resolve()}")
                    package = get_module(module_name=module_name_to_import, module_path=str(plugin_dir.resolve()))
                    plugin_module = getattr(package, "plugin", package)
                    # Determine and store the package name
                    package_name = getattr(package, '__package__', plugin_dir_name)
                    plugin_state.package_name = package_name

                    # STEP 2: Get plugin class
                    plugin_class = next(
                        (cls for _, cls in inspect.getmembers(plugin_module)
                         if inspect.isclass(cls)
                         and issubclass(cls, FastPluggyBaseModule)
                         and cls is not FastPluggyBaseModule),
                        None
                    )

                    if not plugin_class:
                        msg = f"No valid plugin class in {plugin_dir_name} (check __init__.py file)"
                        logger.warning(f"⚠️ {msg}")
                        plugin_state.error.append(msg)
                        plugin_state.plugin = FastPluggyBaseModule(module_name=plugin_dir_name)
                        self.modules[plugin_dir_name] = plugin_state
                        continue

                    # STEP 3: Instantiate
                    plugin_instance = plugin_class()
                    plugin_instance.module_path = plugin_dir

                    plugin_state.plugin = plugin_instance
                    plugin_state.initialized = True
                    plugin_state.enabled = self.plugin_states.get(plugin_instance.module_name, True)
                    # plugin_state.process()

                    self.modules[plugin_instance.module_name] = plugin_state

                    logger.info(f"Plugin '{plugin_instance.module_name}' discovered in {folder}")
                    # if plugin_dir_name != plugin_instance.module_name:
                    #    logger.info(f"Re-key the discovered plugin '{plugin_dir_name}' to '{plugin_instance.module_name}'")
                    #    self.modules[plugin_instance.module_name] = plugin_state

                except Exception as e:
                    err_msg = f"Failed to load plugin '{plugin_dir_name}': {str(e)}"
                    logger.exception(f"🚨 {err_msg}")
                    plugin_state.plugin = FastPluggyBaseModule(module_name=plugin_dir_name)
                    plugin_state.plugin.module_menu_icon = "fas fa-exclamation-triangle"
                    plugin_state.error.append(err_msg)
                    plugin_state.traceback.append(traceback.format_exc())
                    plugin_state.initialized = False
                    plugin_state.process()
                    self.modules[plugin_dir_name] = plugin_state
        else:
            logger.info(f"Missing directory at {folder}")

            # folder_path.mkdir(parents=True, exist_ok=True)
            # create_init_file(folder)

    def discover_plugins_from_entrypoints(self):
        logger.info("🔍 Discovering plugins from entry points (fastpluggy.plugins)")

        # Read and parse FP_PLUGINS: comma-separated names or '*' for all
        fp_env = self.fast_pluggy.settings.fp_plugins.strip()
        if fp_env == "*" or fp_env.lower() == "all":
            allowed = None  # None means “all allowed”
        else:
            allowed = {name.strip() for name in fp_env.split(",") if name.strip()}

        try:
            eps = entry_points(group="fastpluggy.plugins")
        except TypeError:
            eps = entry_points().get("fastpluggy.plugins", [])

        for ep in eps:
            name = ep.name
            # If fp_plugins is set to a specific list, skip any not in that list
            if allowed is not None and name not in allowed:
                logger.info(f"🚫 Skipping '{name}' (not in fp_plugins)")
                continue

            try:
                plugin_class = ep.load()

                if not issubclass(plugin_class, FastPluggyBaseModule):
                    logger.warning(f"🚫 Skipped entry '{name}': Not a FastPluggyBaseModule")
                    continue

                plugin_instance = plugin_class()
                # Resolve path to the module's directory
                plugin_file = Path(sys.modules[plugin_class.__module__].__file__).resolve()
                plugin_path = plugin_file.parent

                # Enabled by default, but you can still override via self.plugin_states
                is_enabled = self.plugin_states.get(plugin_instance.module_name, True)

                # get the version from package
                plugin_instance.module_version = getattr(ep, "dist", None).version if hasattr(ep, "dist") else None
                plugin_state = PluginState(
                    module_type="plugin-pkg",
                    plugin=plugin_instance,
                    path=plugin_path,
                    enabled=is_enabled,
                    initialized=True,
                )
                # plugin_state.process()
                self.modules[plugin_instance.module_name] = plugin_state
                logger.success(
                    f"✅ EntryPoint plugin loaded: {plugin_instance.module_name} from {ep.value}"
                )

            except Exception as e:
                logger.exception(f"❌ Failed to load plugin from entry point '{name}': {e}")
                plugin_state = PluginState(
                    module_type="plugin-pkg",
                    plugin=FastPluggyBaseModule(module_name=name),
                    enabled=False,
                    error=[str(e)],
                    traceback=[traceback.format_exc()]
                )
                plugin_state.plugin.module_menu_icon = "fas fa-exclamation-triangle"
                plugin_state.process()
                self.modules[name] = plugin_state

    def initialize_plugins_in_order(self):
        result = PluginDependencyResolver.get_sorted_modules_by_dependency(self.modules)
        PluginDependencyResolver.update_plugin_states_from_result(result, self.modules)

        if not result["success"]:
            logger.error(f"❌ Dependency resolution failed: {result['error']}")
            return

        for name in result["sorted_modules"]:
            plugin_state = self.modules.get(name)
            if not plugin_state or not plugin_state.enabled and plugin_state.initialized:
                continue

            try:
                # STEP 4: Install deps, git info, etc.
                if self.fast_pluggy.settings.install_module_requirement_at_start:
                    try:
                        PluginService.install_module_requirements(module_name=name, fast_pluggy=self.fast_pluggy)
                    except Exception as install_err:
                        plugin_state.error.append(f"Failed to install requirements: {install_err}")
                        plugin_state.traceback.append(traceback.format_exc())

                #                get_git_info_for_module(module=plugin_state)  # todo make async and avoid fail
                plugin_state.loaded = True
                logger.success(
                    f"✅ Plugin initialized: {plugin_state.plugin.display_name} ({plugin_state.plugin.module_name})")

            except Exception as e:
                logger.exception(f"🚨 Error loading plugin '{name}': {e}")
                plugin_state.error.append(str(e))
                plugin_state.traceback.append(traceback.format_exc())
                plugin_state.plugin = FastPluggyBaseModule(module_name=name)
                plugin_state.plugin.module_menu_icon = "fas fa-exclamation-triangle"
                plugin_state.loaded = False

            finally:
                try:
                    plugin_state.process()
                except Exception as process_err:
                    plugin_state.error.append(f"Error in process(): {process_err}")
                    plugin_state.traceback.append(traceback.format_exc())
                    plugin_state.loaded = False

        return result

    def execute_all_module_hook(self, hook_name: str, require_loaded: bool = True):
        logger.info(f"Executing hook '{hook_name}' (require_loaded:{require_loaded}) for all modules...")
        for module_name, module_info in self.modules.items():
            if not module_info.enabled:
                continue

            if require_loaded and not module_info.loaded:
                logger.warning(f"Skipping hook '{hook_name}' for module '{module_name}' because it is not loaded.")
                continue

            self.call_plugin_hook(plugin_state=module_info, hook_name=hook_name)

    def call_plugin_hook(self, plugin_state: PluginState, hook_name: str, **kwargs):
        plugin = plugin_state.plugin
        if not hasattr(plugin, hook_name):
            return

        hook = getattr(plugin, hook_name)
        if not callable(hook):
            return

        try:
            logger.debug(f"🔧 Calling '{hook_name}' for plugin '{plugin.module_name}'")

            from fastpluggy.fastpluggy import FastPluggy
            call_with_injection(
                func=hook,
                context_dict={
                    FastPluggy: self.fast_pluggy,
                    PluginState: plugin_state,
                    #  BaseModuleManager: self,
                },
                user_kwargs=kwargs
            )

        except Exception as e:
            logger.exception(f"❌ Error in '{hook_name}' of plugin '{plugin.module_name}': {e}")
            plugin_state.error.append(str(e))
            plugin_state.traceback.append(traceback.format_exc())
            plugin_state.plugin.module_menu_icon = "fas fa-exclamation-triangle"

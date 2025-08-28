import os
import sys
import traceback
from pathlib import Path

from fastapi import FastAPI, Depends
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import ChoiceLoader, PackageLoader, Environment, PrefixLoader
from loguru import logger
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.sessions import SessionMiddleware

from fastpluggy import __version__, __SOURCE_COMMIT_CORE__
from fastpluggy.core.auth import require_authentication, require_role
from fastpluggy.core.auth.middleware import CurrentUserMiddleware
from fastpluggy.core.base_module_manager import BaseModuleManager
from fastpluggy.core.config import FastPluggyConfig
from fastpluggy.core.error import  not_found_handler
from fastpluggy.core.error.exception import custom_exception_handler
from fastpluggy.core.flash import FlashMessage, FlashMessageMiddleware
from fastpluggy.core.global_registry import GlobalRegistry
from fastpluggy.core.menu.menu_manager import MenuManager
from fastpluggy.core.routers.app_static import app_static_router
from fastpluggy.core.routers.execute import execute_router
from fastpluggy.core.routers.home import home_router
from fastpluggy.core.routers.ready import ready_router


class FastPluggy(GlobalRegistry):

    def __init__(self, app: FastAPI, app_root_dir=None, path_plugins=None, path_modules=None, auth_manager=None):
        self.module_types = ['plugin', 'domain']
        self.is_ready = False
        self.path_module_types = {"plugin": path_plugins, "domain": path_modules}

        self.app = app

        # init core registry
        self.register_global('list_widget_to_inject', [])

        self.setup_database()
        self.settings = FastPluggyConfig()

        # Add the flash message middleware
        app.add_middleware(FlashMessageMiddleware)
        app.add_middleware(CurrentUserMiddleware)

        self.auth_manager = auth_manager
        if self.auth_manager:
            # app.add_middleware(CurrentUserMiddleware)
            app.add_middleware(AuthenticationMiddleware, backend=self.auth_manager)
        else:
            # TODO look if an auth plugin feature is installed
            logger.warning("No auth manager provided. Fastpluggy will not be able to authenticate users.")

        app.add_middleware(SessionMiddleware, secret_key=self.settings.session_secret_key)

        # Add Exception Handlers
        app.add_exception_handler(Exception, custom_exception_handler)
        app.add_exception_handler(404, not_found_handler)

        self.app_root_dir = str(Path(app_root_dir or ".").resolve())
        sys.path.append(self.app_root_dir)

        self.base_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current file
        self.app.state.fastpluggy = self  # Store in app.state


        self.template_loaders = {}
        self.menu_manager = MenuManager(show_empty_menu_entries=self.settings.show_empty_menu_entries)
        self.app.state.menu_manager = self.menu_manager  # Store in app.state



        try:
            self.load_app()
            self.is_ready = True
            logger.info("Fastpluggy initialized.")
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            traceback.print_exc()
            self.enable_degraded_mode(e)


    def enable_degraded_mode(self, exception: Exception):
        """Enable degraded mode with a fallback router."""
       # self.degraded_mode = True
       # self.degraded_exception = exception

        from fastpluggy.core.error.degraded_mode_handler import DegradedModeHandler
        handler = DegradedModeHandler(exception)
        fallback_router = handler.get_router()

        # Remove all existing routes and install fallback
        self.app.routes.clear()
        self.app.include_router(fallback_router)

    def load_app(self):
        self.template_loaders = {}
        self.menu_manager.init_menu()

        # Call all setup methods automatically in the constructor
        self.configure_static_files()
        self.include_core_route()

        self.module_manager = BaseModuleManager(
            app=self.app, fast_pluggy=self
        )

        # Scan & load modules dynamically
        for module_type in self.module_types:
            folder = self.get_folder_by_module_type(module_type)

            self.module_manager.discover_plugins(folder=folder, module_type=module_type)

        self.module_manager.discover_plugins_from_entrypoints()


        # Load and initialize all plugins in the correct dependency order
        self.module_manager.initialize_plugins_in_order()

        # Update menu creates top level entries
        self.menu_manager.create_module_menu_entries(self.module_manager)

        # Combine template loaders
        self.template_loaders.update(self.module_manager.get_template_loaders())

        self.load_dynamic_route()

        self.configure_templates()
        self.module_manager.execute_all_module_hook(hook_name="after_setup_templates")

        self.menu_manager.update_menu_from_routes(app_routes=self.app.router.routes, module_manager=self.module_manager)

        self.module_manager.execute_all_module_hook(hook_name="on_load_complete")

        self.templates.env.globals['menu_main'] = self.menu_manager.get_menu(menu_type='main')
        self.templates.env.globals['menu_admin'] = self.menu_manager.get_menu(menu_type='admin')

        logger.info("Fastpluggy loaded.")

    def configure_static_files(self):
        """Configure static file serving"""
        static_dir = os.path.join(self.base_dir, "static")  # Relative path to the static directory
        self.app.mount("/static", StaticFiles(directory=static_dir), name="static")

    def configure_templates(self):
        """Configure Jinja2 templates"""

        # Combine base loader and plugin loaders using ChoiceLoader
        loaders = ChoiceLoader(
            [
                PackageLoader("fastpluggy"),
                PrefixLoader(self.template_loaders),
            ]
        )
        jinja_env = Environment(loader=loaders)
        self.templates = Jinja2Templates(env=jinja_env)
        logger.info(f"List of templates : {jinja_env.list_templates()}")

        # Inject plugins as a global variable in Jinja templates
        self.templates.env.globals['version'] = __version__
        #self.templates.env.globals['fp_admin_base_url'] = self.settings.fp_admin_base_url
        self.templates.env.globals['source_commit_core'] = __SOURCE_COMMIT_CORE__
        self.templates.env.globals['app_name'] = self.settings.app_name
        self.templates.env.globals['fp_admin_base_url'] = self.settings.fp_admin_base_url
        self.templates.env.globals['auth_enable'] = bool(self.auth_manager)
        self.templates.env.globals['extra_js_files'] = self.module_manager.get_extra_js_files()
        self.templates.env.globals['extra_css_files'] = self.module_manager.get_extra_css_files()

        from fastpluggy.core.tools.jinja_tools import safe_render
        self.templates.env.globals['safe_render'] = safe_render

        self.templates.env.globals['get_flash_messages'] = FlashMessage.get_flash_messages
        self.templates.env.globals['_'] = lambda x: x  # TODO: setup babel for translate later

        self.app.state.jinja_templates = self.templates

    def setup_database(self):
        """Initialize the database"""
        from fastpluggy.core.database import Base, get_engine

        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            logger.warning("No Database URL provided. Using default database.")
            # todo : add a global warning and maybe a icon it toolbar/menu or a status system somewhere
        try:
            from fastpluggy.core.database import create_table_if_not_exist
            from fastpluggy.core.models import AppSettings
            create_table_if_not_exist(model=AppSettings)
            from fastpluggy.core.models import ModuleRepository
            create_table_if_not_exist(model=ModuleRepository)
        except Exception as e:
            logger.exception(f"Failed to initialize database: {e}")
            self.enable_degraded_mode(e)
            # todo: init minimal mode without database ?

    def include_core_route(self):
        auth_dependencies = []
        if self.auth_manager:
            auth_dependencies.append(Depends(require_authentication))

        if self.settings.admin_enabled:
            base_admin_url = "" if self.settings.fp_admin_base_url == "/" else self.settings.fp_admin_base_url
            self.app.include_router(home_router, dependencies=auth_dependencies, prefix=base_admin_url, include_in_schema=self.settings.include_in_schema_fp)

            admin_deps = auth_dependencies + [require_role("fp_admin")]
            from fastpluggy.core.routers.admin import admin_router
            self.app.include_router(admin_router, dependencies=admin_deps, prefix=base_admin_url,include_in_schema=self.settings.include_in_schema_fp)

            from fastpluggy.core.routers.settings import app_settings_router
            self.app.include_router(app_settings_router, dependencies=admin_deps, prefix=base_admin_url,include_in_schema=self.settings.include_in_schema_fp)

            from fastpluggy.core.routers.base_module import base_module_router
            self.app.include_router(base_module_router, dependencies=admin_deps, prefix=base_admin_url,include_in_schema=self.settings.include_in_schema_fp)

        self.app.include_router(execute_router, dependencies=auth_dependencies, include_in_schema=self.settings.include_in_schema_fp)

        self.app.include_router(ready_router, include_in_schema=self.settings.include_in_schema_fp)

        self.app.include_router(app_static_router, include_in_schema=self.settings.include_in_schema_fp)

    def load_dynamic_route(self):
        # Remove old plugin routes
        routes_to_remove = [
            route for route in self.app.routes
            if isinstance(route, APIRoute) and 'plugin' in route.tags
        ]
        logger.debug(f"routes_to_remove : {routes_to_remove}")

        for route in routes_to_remove:
            self.app.routes.remove(route)
            logger.info(f"Removed route '{route.path}'.")

        # Register new module routes
        self.module_manager.register_all_routes()

    def get_manager(self) -> BaseModuleManager:
        """
        Helper function to retrieve the manager based on the type of module.
        """
        return self.module_manager

    def get_folder_by_module_type(self, type_module: str) -> str|None:
        """
        Helper function to retrieve the manager based on the type of module.
        """
        if type_module in self.module_types:
            if self.path_module_types[type_module] is not None:
                return self.path_module_types[type_module]
            else:
                return f'{self.app_root_dir}/{type_module}s'

        else:
            logger.error(f"Type of module '{type_module}' not supported.")
            return None

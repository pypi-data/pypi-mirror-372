from typing import List, Optional, Dict, Any

from fastapi.routing import APIRoute, APIRouter
from loguru import logger

from fastpluggy.core.base_module_manager import BaseModuleManager
from fastpluggy.core.menu.schema import MenuItem


class MenuManager:
    def __init__(self, show_empty_menu_entries: bool = True):
        self.show_empty_menu_entries = show_empty_menu_entries
        self.menus: Dict[str, List[MenuItem]] = {}
        self.init_menu()

    def init_menu(self):
        self.menus = {
            "main": [],
            "user": [],
            "admin": [],
            "no": []
        }

    def add_parent_item(self, menu_type: str, item: MenuItem):
        """
        Creates a parent entry in the specified menu group.
        This function is used in module auto-detection to create an empty submenu.
        It only adds the parent entry if one with the same parent_name does not already exist.

        :param menu_type: The menu group ("main", "user", "admin", "no").
        :param item: A MenuItem instance that represents the parent entry.
                     Its `parent_name` field should be set (and will be used as the parent's identifier).
        """
        if menu_type not in self.menus:
            raise ValueError(f"Invalid menu type: {menu_type}")

        if not item.parent_name:
            logger.info("No parent_name provided in the item; cannot add as a parent entry.")
            return

        # Check if a parent entry with the same identifier already exists.
        existing_parent = next((m for m in self.menus[menu_type] if m.parent_name == item.parent_name), None)
        if existing_parent:
            logger.info(f"Parent entry '{item.parent_name}' already exists in the {menu_type} menu")
            return existing_parent
        else:
            # Add the provided item as the parent entry.
            self.menus[menu_type].append(item)
            logger.info(f"Created new parent entry '{item.parent_name}' in the {menu_type} menu")

    def add_menu_item(self, menu_type: str, item: MenuItem):
        if menu_type not in self.menus:
            raise ValueError(f"Invalid menu type: {menu_type}")

        if item.parent_name:
            parent_item = next((m for m in self.menus[menu_type] if m.parent_name == item.parent_name), None)
            if parent_item:
                parent_item.add_child(item)
                return

        existing = next((m for m in self.menus[menu_type] if m.url == item.url), None)
        if not existing:
            self.menus[menu_type].append(item)

    def get_menu(self, menu_type: str, current_url: Optional[str] = None) -> List[Dict[str, Any]]:
        if menu_type not in self.menus:
            raise ValueError(f"Invalid menu type: {menu_type}")

        result = []
        for index, item in enumerate(self.menus[menu_type]):
            is_valid_url = item.url and item.url != "#"
            is_non_empty_dropdown = item.is_dropdown() and any(
                child.url and child.url != "#" for child in item.children
            )

            if not self.show_empty_menu_entries and not (is_valid_url or is_non_empty_dropdown):
                continue

            result_item = item.to_dict(current_url)
            result.append(result_item)

        sorted_items = sorted(result, key=lambda x: x.get("position") if x.get("position") is not None else 9999)
        return sorted_items

    def update_menu_from_routes(self, app_routes: List[APIRoute],
                                module_manager: BaseModuleManager,  # <— now pass this in
                                menu_type: str = "main", ):
        if menu_type not in self.menus:
            raise ValueError(f"Invalid menu type: {menu_type}")

        for route in app_routes:
            if not (isinstance(route, APIRoute) and hasattr(route.endpoint, "_menu_entry")):
                continue

            entry = route.endpoint._menu_entry
            target_menu = entry.get("type", menu_type)

            # infer parent from module path if not explicitly set
            parent = entry.get("parent")
            if parent is None:
                parent_module = get_plugin_state_for_route(route, module_manager.modules.values())
                print(parent_module)
                parent = parent_module.plugin.module_name if parent_module else None

            item = MenuItem(
                label=entry["label"],
                url=route.path,
                icon=entry.get("icon"),
                parent_name=parent,
                permission=entry.get("permission"),
                position=entry.get("position"),
                section_title=entry.get("section_title"),
                divider_before=entry.get("divider_before", False),
                divider_after=entry.get("divider_after", False),
            )
            self.add_menu_item(target_menu, item)
            logger.info(
                f"Added route '{route.path}' to '{target_menu}' "
                f"menu with label '{entry['label']}' under parent '{parent}'"
            )

    def create_module_menu_entries(self, module_manager):
        """
        Updates the provided MenuManager with entries for the loaded modules, to have the main entry.
        The sub link/menu will be added using update_menu_from_routes by scanning routes.
        """
        for module_info in module_manager.modules.values():
            if module_manager.is_module_loaded(module_info):
                self.add_parent_item(
                    item=MenuItem(
                        label=module_info.plugin.display_name,
                        url=module_info.url,
                        icon=module_info.plugin.module_menu_icon,
                        parent_name=module_info.plugin.module_name,
                    ),
                    menu_type=module_info.plugin.module_menu_type,
                )


def get_plugin_state_for_route(
        route_to_match: APIRoute,
        modules: List["PluginState"],
) -> Optional["PluginState"]:  # Replace Any with PluginState
    """
    Given a request path, scan through a list of modules, inspect each module's APIRouter,
    and return the module's PluginState if one of its routes matches the given path.

    :param route_path: The incoming request path (e.g., '/items/123')
    :param modules: A list of module objects, each expected to have attributes:
                    - router: an APIRouter instance or a list of APIRouter instances
                    - plugin_state: the PluginState instance for that module
    :return: The matching module's PluginState, or None if no match is found.
    """
    for module in modules:
        plugin = getattr(module, "plugin", None)
        plugin_router = getattr(plugin, "module_router", None)

        # Handle case where plugin_router is a list of routers
        if isinstance(plugin_router, list) and plugin_router is not None:
            for router in plugin_router:
                if isinstance(router, APIRouter):
                    for route in router.routes:
                        if isinstance(route, APIRoute):
                            if route_to_match.endpoint == route.endpoint:
                                return module
        # Handle case where plugin_router is a single router
        elif isinstance(plugin_router, APIRouter) and plugin_router is not None:
            for route in plugin_router.routes:
                if isinstance(route, APIRoute):
                    if route_to_match.endpoint == route.endpoint:
                        return module
    return None

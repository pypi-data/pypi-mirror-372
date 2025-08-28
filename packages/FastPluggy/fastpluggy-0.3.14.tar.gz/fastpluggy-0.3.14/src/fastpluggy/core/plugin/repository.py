from typing import Dict, Optional

from loguru import logger
from sqlalchemy.orm import Session

from fastpluggy.core.models import ModuleRepository
#from fastpluggy.core.tools.git_tools import GitInfo


def update_plugin_status(db: Session, plugin_name: str, status: bool) -> bool:
    """
    Update the status of a plugin in the database.

    :param db: The database session.
    :param plugin_name: The name of the plugin.
    :param status: The new status of the plugin (True for enabled, False for disabled).
    :return: True if the plugin's status was updated successfully, False otherwise.
    """
    # Check if the plugin exists in the database
    plugin = db.query(ModuleRepository).filter_by(name=plugin_name).first()

    if plugin is None:
        logger.error(f"Plugin '{plugin_name}' does not exist in the database.")
        plugin = ModuleRepository(name=plugin_name)

    # Update the plugin status
    plugin.active = status
    db.add(plugin)
    db.commit()

    logger.info(f"Plugin '{plugin_name}' status updated to {status}.")
    return True


def get_all_modules_status(db: Session) -> Dict[str, bool]:
    """
    Retrieves plugin status from the database and populates the plugin_states dictionary.
    """
    plugin_states = {}
    if not db:
        logger.warning("Database session is not set for PluginManager.")
        return plugin_states

    module_records = db.query(ModuleRepository).all()
    if module_records:
        plugin_states = {module.name: module.active for module in module_records}

    logger.info(f"Loaded plugin states: {plugin_states}")

    return plugin_states



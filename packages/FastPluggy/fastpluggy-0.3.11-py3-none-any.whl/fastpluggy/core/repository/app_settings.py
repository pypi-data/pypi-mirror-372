from loguru import logger

from fastpluggy.core.database import session_scope
from fastpluggy.core.models import AppSettings
from fastpluggy.core.tools import convert_param_type



def set_app_setting(db, current_settings, key, value):
    """
    Set a key-value pair in the AppSettings table, ensuring no duplicates for the same namespace and key.

    Args:
        db: The database session object.
        current_settings: The current settings object.
        key (str): The key to set or update.
        value: The value to set for the key.
    """
    namespace = current_settings.__class__.__name__
    existing_item = db.query(AppSettings).filter_by(namespace=namespace, key=key).first()
    param_type = type(getattr(current_settings, key))
    converted_value =  convert_param_type(param_type, value)

    if existing_item:
        # Update the existing item's value
        existing_item.value = converted_value
        existing_item.value_type=param_type.__name__
    else:
        # Create a new item
        item = AppSettings(
            namespace=namespace, key=key,
            value=converted_value,
            value_type=param_type.__name__,
        )
        db.add(item)

    db.commit()

    setattr(current_settings, key, value)


def fetch_settings_from_database(settings_class, namespace: str):
    settings_dict = {}

    try:
        with session_scope() as session:
            settings = session.query(AppSettings).filter_by(namespace=namespace).all()
            for setting in settings:
                # Use the `convert_param_type` function to handle type conversion
                if setting.key in settings_class.model_fields:
                    settings_dict[setting.key] = convert_param_type(setting.value_type, setting.value)
                else:
                    logger.warning(f"Key '{setting.key}' not found in settings class '{settings_class.__name__}'.")
    except Exception as e:
        logger.exception("Error while fetching settings from database", e)

    return settings_dict


def update_db_settings(current_settings, db, new_params: dict):

    logger.debug(f"Submitted form data: {new_params}")

    new_values = {
        key: convert_param_type(type(getattr(current_settings, key)), new_params.get(key))
        for key in new_params
        if convert_param_type(type(getattr(current_settings, key)), new_params.get(key))
           != getattr(current_settings, key)
    }
    logger.info(f"New values to update: {new_values}")

    for key, value in new_values.items():
        set_app_setting(db, current_settings, key, value)

from fastpluggy.core.config import FastPluggyConfig
from fastpluggy.core.database import create_table_if_not_exist
from fastpluggy.core.models import AppSettings
from fastpluggy.core.repository.app_settings import set_app_setting


def test_set_app_setting(db_session):
    # Create a FastPluggyConfig instance
    create_table_if_not_exist(AppSettings)
    settings = FastPluggyConfig()

    # Initial settings
    key = "app_name"
    value = "TestApp"

    # Call set_app_setting
    set_app_setting(db_session, settings, key, value)

    # Validate database state
    saved_item = db_session.query(AppSettings).filter_by(key=key).first()
    assert saved_item is not None, "AppSettings entry was not created in the database."
    assert saved_item.namespace == "FastPluggyConfig"
    assert saved_item.key == key
    assert saved_item.value == value
    assert saved_item.value_type == type(settings.app_name).__name__

    # Validate settings update
    assert settings.app_name == value

    # Update the same setting
    new_value = "UpdatedTestApp"
    set_app_setting(db_session, settings, key, new_value)

    # Validate database update
    updated_item = db_session.query(AppSettings).filter_by(key=key).first()
    assert updated_item.value == new_value, "AppSettings entry was not updated in the database."
    assert settings.app_name == new_value

    set_app_setting(db_session, settings, 'install_module_requirement_at_start', 'n')

    # Verify settings were saved to the database correctly
    app_name_setting = db_session.query(AppSettings).filter_by(key='app_name').first()
    assert app_name_setting is not None
    assert app_name_setting.value == new_value

    install_setting = db_session.query(AppSettings).filter_by(key='install_module_requirement_at_start').first()
    assert install_setting is not None
    assert install_setting.value == 'false'

    settings_check = FastPluggyConfig()
    assert settings_check.app_name == new_value
    assert settings_check.install_module_requirement_at_start == False
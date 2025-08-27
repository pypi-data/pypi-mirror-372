from typing import Optional, Tuple, Type, Any, Dict

from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource
from fastpluggy.core.repository.app_settings import fetch_settings_from_database


class DatabaseSettingsSource(PydanticBaseSettingsSource):
    """
    A Pydantic v2 settings source that loads values from your database
    via your existing `fetch_settings_from_database` function.
    """

    def __init__(self, settings_cls: Type[BaseSettings]):
        super().__init__(settings_cls=settings_cls)
        self._loaded: Dict[str, Any] | None = None

    def _ensure_loaded(self) -> None:
        if self._loaded is None:
            # Pull everything in one go
            self._loaded = fetch_settings_from_database(
                settings_class=self.settings_cls,
                namespace=self.settings_cls.__name__,
            )

    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> Tuple[Any, str, bool]:
        """
        Called by Pydantic for each field.
        Return (value, key_to_set, value_is_complex).
        """
        self._ensure_loaded()
        value = self._loaded.get(field_name)
        return value, field_name, False

    def prepare_field_value(
            self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool
    ) -> Any:
        # You could do extra per‐field conversion here
        return value

    def __call__(self) -> Dict[str, Any]:
        """
        Pydantic invokes this once to collect all values.
        We loop over the model_fields and pull from our loaded dict.
        """
        result: Dict[str, Any] = {}
        for name, field in self.settings_cls.model_fields.items():
            val, key, _ = self.get_field_value(field, name)
            if val is not None:
                result[key] = self.prepare_field_value(name, field, val, False)
        return result

class BaseDatabaseSettings(BaseSettings):
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        # Call your DB source factory with the settings class so it returns a proper source
        db_source = DatabaseSettingsSource(settings_cls)

        return (
            init_settings,         # 1. Explicit kwargs
            env_settings,          # 2. Env vars
            dotenv_settings,       # 3. .env files
            file_secret_settings,  # 4. Secret files
            db_source,             # 5. Your custom DB-backed source
        )


class FastPluggyConfig(BaseDatabaseSettings):
    app_name: Optional[str] = 'FastPluggy'
    debug: Optional[bool] = False

    # admin config
    admin_enabled: Optional[bool] = True
    fp_install_enabled: Optional[bool] = True
    fp_admin_base_url: Optional[str] = '/admin'
    fp_plugins: Optional[str] = '*'
    include_in_schema_fp: Optional[bool] = True
    plugin_list_url: Optional[str] = 'https://registry.fastpluggy.xyz/plugins.json'

    show_empty_menu_entries: Optional[bool] = True
    install_module_requirement_at_start: Optional[bool] = True

    session_secret_key: str = "your-secret-key"

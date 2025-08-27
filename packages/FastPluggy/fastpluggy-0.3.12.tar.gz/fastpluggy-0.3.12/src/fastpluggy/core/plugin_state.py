import logging
import traceback
import types
from pathlib import Path
from typing import Optional, Any, List

from pydantic import BaseModel, Field, computed_field

from fastpluggy.core.module_base import FastPluggyBaseModule
#from fastpluggy.core.tools.git_tools import GitInfo


class PluginState(BaseModel):
    plugin: Optional[FastPluggyBaseModule] = None
    path: Optional[Path] = None
    initialized: bool = False  # only load of plugin.py
    loaded: bool = False  # fully setup
    enabled: bool = True  # enabled by user

    error: List[str] = Field(default_factory=list)
    warning: List[str] = Field(default_factory=list)
    dependency_issues: List[Any] = Field(default_factory=list)
    traceback: List[Any] = Field(default_factory=list)

    # module: Optional[ModuleType] = None
    module_type: Optional[str] = None
    package_name: Optional[str] = None

    settings: Optional[Any] = None

    @computed_field
    @property
    def git_available(self) -> bool:
        if self.path:
            git_path = Path(self.path) / ".git"
            return git_path.exists()
        return False

    #git_info: Optional[GitInfo] = None

    requirements_installed: Optional[bool] = None
    # todo : check if requirement are already installed

    # --- Extra data ---
    extra_data: dict = Field(
        default_factory=dict,
        description="Additional data that can be stored by the module. "
                    "Used for storing custom data that can be accessed by the module or other modules. "
                    "Structure: key -> {name: str, panel: bool, data: Any}"
    )

    class Config:
        arbitrary_types_allowed = True

    def to_dict(self):
        data_plugin = self.plugin.model_dump() if self.plugin else {}
        data_self = self.model_dump(exclude={"plugin"})
        return {**data_self, **data_plugin}

    @computed_field
    @property
    def have_update(self) -> bool:
        #if self.git_info is not None:
        #    return self.git_info.have_update
        return False

    @computed_field
    @property
    def url(self) -> str:
        if self.plugin is not None:
            return f"/{self.module_type}/{self.plugin.module_name}"
        else:
            return "#"

    @computed_field
    @property
    def status_html(self) -> str:
        if self.warning:
            return f'<span class="badge bg-warning" title="{" / ".join(self.warning)}">Warning</span>'
        if self.error:
            return f'<span class="badge bg-danger" title="{" / ".join(self.error)}">Failed</span>'
        if self.dependency_issues:
            return f'<span class="badge bg-secondary" title="{" / ".join(self.dependency_issues)}">Dependency issues</span>'
        if self.loaded:
            return '<span class="badge bg-green">Enabled</span>' if self.enabled else '<span class="badge bg-red">Disabled</span>'
        return '<span class="badge bg-secondary">Not loaded!</span>'

    @computed_field
    @property
    def version_html(self) -> str:
        version = []
        if self.plugin and self.plugin.module_version:
            version.append(self.plugin.module_version)
        #if self.git_info and self.git_info.current_version:
        #    version.append(self.git_info.current_version[:8])
        return " - ".join(version) if version else "N/A"

    def process(self):
        if self.plugin is None:
            logging.error(f"Plugin {self} not loaded")
            self.plugin = FastPluggyBaseModule()
        self.plugin.module_path = self.path

        # change icon on error
        if self.error:
            self.plugin.module_menu_icon = "fas fa-exclamation-triangle"

        # init settings
        if self.plugin and self.enabled and self.plugin.module_settings:
            if not isinstance(self.plugin.module_settings, type):
                self.error.append("Settings should be a class, not instance.")
            else:
                try:
                    self.settings = self.plugin.module_settings()
                except Exception as err:
                    self.error.append(f"Could not initialize settings: {err}")
                    self.traceback.append(traceback.format_exc())

        # If router of module is a function, call it/update
        if isinstance(self.plugin.module_router, types.FunctionType):
            try:
                self.plugin.module_router = self.plugin.module_router()
            except Exception as err:
                logging.error(f"Could not initialize router: {err}")
                self.error.append(f"Could not initialize router: {err}")
                self.plugin.module_router = None
                raise err
        # todo : mode init of enable status here

    def add_warning(self, warning: str):
        self.warning.append(warning)

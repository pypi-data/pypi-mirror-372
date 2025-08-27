from sqlalchemy import Column, String, Boolean, Text, DateTime, func
from sqlalchemy import Integer

from fastpluggy.core.database import Base


class AppSettings(Base):
    __tablename__ = 'fp_core_app_settings'

    id = Column(Integer, primary_key=True)
    namespace = Column(String(255), nullable=False)
    key = Column(String(255), nullable=False)
    value = Column(Text, nullable=False)
    value_type = Column(String(50), nullable=False, default="string")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class ModuleRepository(Base):
    __tablename__ = 'fp_core_module_repository'

    name = Column(String(255), unique=True, nullable=False)  # Plugin name
    git_url = Column(String(255), nullable=True)  # Git repository URL for the plugin
    current_version = Column(String(255), nullable=True)  # Git hash of the current version
    active = Column(Boolean, default=True)  # Whether the plugin is active
    last_version = Column(String(255), nullable=True)  # Git hash of the last version found


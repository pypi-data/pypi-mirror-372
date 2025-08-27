from collections import OrderedDict
from typing import Any


class GlobalRegistry:
    _global_registry: dict[str, Any] = {}

    @classmethod
    def register_global(cls, key: str, obj: Any):
        cls._global_registry[key] = obj

    @classmethod
    def get_global(cls, key: str, default=None) -> Any:
        return cls._global_registry.get(key, default)

    @classmethod
    def has_global(cls, key: str) -> bool:
        return key in cls._global_registry

    @classmethod
    def extend_globals(cls, key: str, items: Any):
        if isinstance(items, dict):
            if key not in cls._global_registry:
                cls._global_registry[key] = {}
            cls._global_registry[key].update(items)
        if isinstance(items, list):
            existing = cls._global_registry.setdefault(key, [])
            merged = existing + items
            try:
                cls._global_registry[key] = list(OrderedDict.fromkeys(merged))
            except TypeError:
                cls._global_registry[key] = list(merged)

    @classmethod
    def get_all_globals(cls) -> dict[str, Any]:
        return dict(cls._global_registry)

    @classmethod
    def clear_globals(cls):
        cls._global_registry.clear()

    @classmethod
    def clear_globals_key(cls, key):
        if key in cls._global_registry:
            del cls._global_registry[key]

from dataclasses import dataclass, asdict
from typing import Optional, Any, Type


@dataclass
class FieldMeta:
    type: Any
    required: bool
    readonly: bool
    default: Any
    description: Optional[str] = None
    primary_key: Optional[bool] = False
    enum_class: Optional[Type] = None

    def to_dict(self) -> dict:
        return asdict(self)

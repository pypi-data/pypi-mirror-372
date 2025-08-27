from typing import Optional, List, Dict, Any

from loguru import logger
from typing import Self
from pydantic import BaseModel, Field

class MenuItem(BaseModel):
    label: str
    url: Optional[str] = '#'
    icon: Optional[str] = None
    parent_name: Optional[str] = None
    permission: Optional[str] = None
    position: Optional[int] = None
    section_title: Optional[str] = None
    divider_before: bool = False
    divider_after: bool = False
    children: List[Self] = Field(default_factory=list)

    model_config = {
        "arbitrary_types_allowed": True,
    }


    def add_child(self, child: 'MenuItem') -> bool:
        if any(existing.url == child.url for existing in self.children):
            logger.info(f"Child with URL '{child.url}' already exists under '{self.label}'. Skipping.")
            return False
        self.children.append(child)
        return True

    def is_dropdown(self) -> bool:
        return bool(self.children)

    def __repr__(self)->str:
        return f"<MenuItem label={self.label} url={self.url} icon={self.icon} parent_name={self.parent_name} permission={self.permission} position={self.position}  children={self.children}>"

    def to_dict(self, current_url: Optional[str] = None) -> Dict[str, Any]:
        item_dict = {
            "label": self.label,
            "url": self.url,
            "icon": self.icon,
            "parent_name": self.parent_name,
            "permission": self.permission,
            "position": self.position,
            "section_title": self.section_title,
            "divider_before": self.divider_before,
            "divider_after": self.divider_after,
            "active": self.url == current_url,
        }
        if self.is_dropdown():
            sorted_children = sorted(
                self.children,
                key=lambda child: child.position if child.position is not None else 9999
            )
            item_dict["children"] = [child.to_dict(current_url) for child in sorted_children]
        return item_dict

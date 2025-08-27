from functools import wraps
from typing import Optional

def menu_entry(
    label: str,
    icon: str = "fa fa-ask",
    parent: Optional[str] = None,
    type: str = "main",
    position: Optional[int] = None,
    #section_title: Optional[str] = None,
    divider_before: bool = False,
    divider_after: bool = False,
    permission: Optional[str] = None,
):
    """
    set parent to make a top entry if we set a value not named like a plugin
    Usage:
    @menu_entry(
        label="Dashboard",
        icon="fas fa-tachometer-alt",
        position=1,
        divider_before=True
    )
    """

    def decorator(func):
        func._menu_entry = {
            "label": label,
            "type": type,
            "icon": icon,

            "parent": parent ,

            "position": position,
           # "section_title": section_title,
            "divider_before": divider_before,
            "divider_after": divider_after,
            "permission": permission,
        }

        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        return wrapper

    return decorator

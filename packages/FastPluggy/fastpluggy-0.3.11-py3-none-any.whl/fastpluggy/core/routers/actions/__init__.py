
from typing import Annotated

from fastpluggy.core.flash import FlashMessage
from fastpluggy.core.tools.inspect_tools import InjectDependency
from fastpluggy.fastpluggy import FastPluggy


def reload_fast_pluggy(fast_pluggy: Annotated[FastPluggy, InjectDependency]):
    fast_pluggy.load_app()
    return FlashMessage(message="FastPluggy reinstalled successfully!", category="success")


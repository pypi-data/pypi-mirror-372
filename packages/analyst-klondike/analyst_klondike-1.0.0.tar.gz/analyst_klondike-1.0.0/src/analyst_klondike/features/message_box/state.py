from typing import Callable
from dataclasses import dataclass


@dataclass
class MessageBoxState:
    is_visible: bool = False
    message: str = ""
    ok_button_callback: Callable[[], None] | None = None

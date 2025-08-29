from typing import Callable
from dataclasses import dataclass
from analyst_klondike.state.base_action import BaseAction


@dataclass
class DisplayMessageBoxAction(BaseAction):
    type = "DISPLAY_MESSAGE_BOX_ACTION"
    message: str
    ok_button_callback: Callable[[], None] | None = None


@dataclass
class HideMessageBoxAction(BaseAction):
    type = "HIDE_MESSAGE_BOX_ACTION"

from dataclasses import dataclass

from analyst_klondike.state.base_action import BaseAction


@dataclass
class DisableEvents(BaseAction):
    type = "DISABLE_EVENTS_ACTION"

from analyst_klondike.features.message_box.actions import (
    DisplayMessageBoxAction,
    HideMessageBoxAction
)
from analyst_klondike.state.app_state import AppState
from analyst_klondike.state.base_action import BaseAction


def apply(state: AppState, action: BaseAction) -> AppState:
    if isinstance(action, DisplayMessageBoxAction):
        state.message_box.is_visible = True
        state.message_box.message = action.message
        state.message_box.ok_button_callback = action.ok_button_callback
        return state
    if isinstance(action, HideMessageBoxAction):
        state.message_box.is_visible = False
        return state
    return state

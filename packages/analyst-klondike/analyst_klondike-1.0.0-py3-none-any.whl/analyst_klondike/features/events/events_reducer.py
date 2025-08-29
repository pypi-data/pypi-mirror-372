from analyst_klondike.features.code_import.ui_actions.actions import SwitchToTeacherModeAction
from analyst_klondike.features.events.event_actions import DisableEvents
from analyst_klondike.state.app_state import AppState
from analyst_klondike.state.base_action import BaseAction


def apply(state: AppState, action: BaseAction) -> AppState:
    if isinstance(action, DisableEvents):
        state.event_sender = "no_events"
    if isinstance(action, SwitchToTeacherModeAction):
        state.is_teacher_mode = True
    return state

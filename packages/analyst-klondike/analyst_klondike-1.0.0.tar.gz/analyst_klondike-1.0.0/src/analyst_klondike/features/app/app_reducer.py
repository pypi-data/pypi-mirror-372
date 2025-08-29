from analyst_klondike.features.app.actions import ChangeAppTitleAction, ChangeThemeAction, EditorScreenReadyAction
from analyst_klondike.state.app_state import AppState
from analyst_klondike.state.base_action import BaseAction


def apply(state: AppState, action: BaseAction) -> AppState:
    if isinstance(action, ChangeThemeAction):
        state.theme = action.theme
        state.is_dark = action.is_dark
        return state
    if isinstance(action, EditorScreenReadyAction):
        state.is_editor_screen_ready = True
        return state
    if isinstance(action, ChangeAppTitleAction):
        state.current.app_title = action.title
        state.current.app_subtitle = action.sub_title
    return state

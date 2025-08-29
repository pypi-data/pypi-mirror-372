from analyst_klondike.features.data_context.init_action import (
    InitAction,
    ReadFileAndAppVersion,
    init_file_and_app_version,
    init_state)
from analyst_klondike.features.data_context.set_opened_file_action import SetOpenedFileAction
from analyst_klondike.state.app_state import AppState
from analyst_klondike.state.base_action import BaseAction


def apply(state: AppState, action: BaseAction) -> AppState:
    if isinstance(action, InitAction):
        init_state(state, action.data)
        return state
    if isinstance(action, SetOpenedFileAction):
        state.current.opened_file_path = action.opened_file_path
        state.current.opened_file_name = action.opened_file_name
        return state
    if isinstance(action, ReadFileAndAppVersion):
        init_file_and_app_version(state, action.data)
    return state

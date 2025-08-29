from analyst_klondike.features.code import code_reducer
from analyst_klondike.features.code_explorer import code_explorer_reducer

from analyst_klondike.features.data_context import load_file_reducer
from analyst_klondike.features.app import app_reducer
from analyst_klondike.features.message_box import message_box_reducer
from analyst_klondike.features.code_import.ui_actions import code_import_reducer
from analyst_klondike.features.events import events_reducer
from analyst_klondike.state.app_state import dispatch

from analyst_klondike.state.base_action import BaseAction


def app_dispatch(action: BaseAction):
    dispatch(action,
             load_file_reducer.apply,
             code_explorer_reducer.apply,
             code_reducer.apply,
             app_reducer.apply,
             message_box_reducer.apply,
             code_import_reducer.apply,
             events_reducer.apply
             )

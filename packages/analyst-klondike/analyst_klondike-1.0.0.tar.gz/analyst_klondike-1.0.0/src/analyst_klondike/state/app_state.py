from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Callable, Literal
from analyst_klondike.features.code.state import RunCodeState
from analyst_klondike.features.current.current_state import CurrentState
from analyst_klondike.features.data_context.data_state import DataState
from analyst_klondike.features.message_box.state import MessageBoxState
from analyst_klondike.state.base_action import BaseAction


@dataclass
class Enable:
    run_code_button: bool
    open_file_button: bool


@dataclass
class AppState:
    last_action_type: str
    user_email: str
    theme: str
    is_dark: bool
    is_editor_screen_ready: bool
    event_sender: Literal["local_file", "local_db", "remote_db", "no_events"]
    data: DataState
    current: CurrentState
    run_code: RunCodeState
    message_box: MessageBoxState
    is_teacher_mode: bool


INITIAL_STATE = AppState(
    user_email="",
    theme="",
    is_dark=True,
    is_editor_screen_ready=False,
    data=DataState(),
    current=CurrentState(),
    run_code=RunCodeState(),
    message_box=MessageBoxState(),
    last_action_type="",
    event_sender="remote_db",
    is_teacher_mode=False
)


_state = INITIAL_STATE


def get_state() -> AppState:
    return select(lambda _: _state)


Reducers = Callable[[AppState, BaseAction], AppState]


def dispatch(action: BaseAction, *reducers: Reducers) -> None:
    state = get_state()
    copy_state = deepcopy(state)
    copy_state.last_action_type = action.type
    # pylint: disable=global-statement
    global _state
    _state = _pipe(copy_state, action, *reducers)
    # pylint: disable=import-outside-toplevel
    from analyst_klondike.ui.runner_app import get_app
    app = get_app()
    app.update_view(_state)


def select(selector: Callable[[AppState], Any]) -> Any:
    return selector(_state)


def _pipe(state: AppState,
          action: BaseAction,
          *reducers: Callable[[AppState, BaseAction], AppState]) -> AppState:
    s = state
    for apply in reducers:
        s = apply(s, action)
    return s

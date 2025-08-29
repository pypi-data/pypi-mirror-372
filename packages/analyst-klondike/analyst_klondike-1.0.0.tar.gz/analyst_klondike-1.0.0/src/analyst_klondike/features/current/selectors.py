from analyst_klondike.features.data_context.data_state import (
    PythonQuizState,
    PythonTaskState
)
from analyst_klondike.state.app_state import AppState


def select_current_task(state: AppState) -> PythonTaskState | None:
    curr_id = state.current.task_id
    if curr_id is None:
        return None
    return state.data.tasks[curr_id]


def select_current_quiz(state: AppState) -> PythonQuizState | None:
    curr_id = state.current.quiz_id
    if curr_id is None:
        return None
    return state.data.quizes[curr_id]


def select_has_file_openned(state: AppState) -> bool:
    return state.current.opened_file_name != ""

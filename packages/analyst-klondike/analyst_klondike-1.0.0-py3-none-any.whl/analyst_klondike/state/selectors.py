from analyst_klondike.features.data_context.data_state import (
    PythonQuizState,
    PythonTaskState
)
from analyst_klondike.state.app_state import AppState


def select_task_by_id(state: AppState, task_id: int) -> PythonTaskState:
    if task_id not in state.data.tasks:
        raise KeyError(f"{task_id} not exists")
    return state.data.tasks[task_id]


def select_quiz_by_id(state: AppState, quiz_id: str) -> PythonQuizState:
    if quiz_id not in state.data.quizes:
        raise KeyError(f"{quiz_id} not exists")
    return state.data.quizes[quiz_id]


def select_tasks_for_quiz(state: AppState, quiz_id: str):
    return (t for t in state.data.tasks.values()
            if t.quiz_id == quiz_id)

from analyst_klondike.features.code_import.ui_actions.actions import ImportTasksAction
from analyst_klondike.features.data_context.data_state import PythonTaskState
from analyst_klondike.state.app_state import AppState
from analyst_klondike.state.base_action import BaseAction


def apply(state: AppState, action: BaseAction) -> AppState:
    if isinstance(action, ImportTasksAction):
        max_task_id = max(t.id for t
                          in state.data.tasks.values())
        task_id = max_task_id + 1
        _remove_with_the_same_title_tasks(action.tasks, state)

        for task in action.tasks:
            task.id = task_id
            state.data.tasks[task_id] = task
            task_id += 1
    return state


def _remove_with_the_same_title_tasks(tasks: list[PythonTaskState], state: AppState):
    imported_tasks_titles = [t.title for t in tasks]
    sorted_dict = {
        k: v for k, v in state.data.tasks.items()
        if v.title not in imported_tasks_titles
    }
    state.data.tasks = sorted_dict

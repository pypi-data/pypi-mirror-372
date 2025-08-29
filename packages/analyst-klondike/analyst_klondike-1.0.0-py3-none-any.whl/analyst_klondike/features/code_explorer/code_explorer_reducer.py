from analyst_klondike.features.code_explorer.actions import (
    QuizNodeCollapseAction,
    QuizNodeExpandAction
)
from analyst_klondike.features.current.actions import (
    MakeQuizCurrentAction,
    MakeTaskCurrentAction,
)
from analyst_klondike.state.app_state import AppState
from analyst_klondike.state.base_action import BaseAction
from analyst_klondike.state.selectors import (
    select_quiz_by_id,
    select_task_by_id
)


def apply(state: AppState, action: BaseAction) -> AppState:
    if isinstance(action, QuizNodeExpandAction):
        quiz = state.data.quizes[action.quiz_id]
        quiz.is_node_expanded = True
        return state
    if isinstance(action, QuizNodeCollapseAction):
        quiz = state.data.quizes[action.quiz_id]
        quiz.is_node_expanded = False
        return state
    if isinstance(action, MakeTaskCurrentAction):
        state.current.task_id = action.task_id
        state.current.quiz_id = None
        # set code to run
        curr_task = select_task_by_id(state, action.task_id)
        state.run_code.last_code = curr_task.code
        state.current.app_subtitle = curr_task.title
        state.current.object_name = "task"
        return state
    if isinstance(action, MakeQuizCurrentAction):
        state.current.quiz_id = action.quiz_id
        state.current.task_id = None
        quiz = select_quiz_by_id(state, action.quiz_id)
        state.current.app_subtitle = quiz.title
        state.current.object_name = "quiz"
        return state
    return state

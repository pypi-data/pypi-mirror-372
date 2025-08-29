from dataclasses import dataclass

from analyst_klondike.state.base_action import BaseAction


@dataclass
class MakeTaskCurrentAction(BaseAction):
    type = "MAKE_TASK_CURRENT"
    task_id: int


@dataclass
class MakeQuizCurrentAction(BaseAction):
    type = "MAKE_QUIZ_CURRENT"
    quiz_id: str

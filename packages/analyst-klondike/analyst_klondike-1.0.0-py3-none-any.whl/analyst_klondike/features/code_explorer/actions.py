from dataclasses import dataclass

from analyst_klondike.state.base_action import BaseAction


@dataclass
class QuizNodeExpandAction(BaseAction):
    type = "QuizNodeExpand"
    quiz_id: str


@dataclass
class QuizNodeCollapseAction(BaseAction):
    type = "QuizNodeCollapsed"
    quiz_id: str

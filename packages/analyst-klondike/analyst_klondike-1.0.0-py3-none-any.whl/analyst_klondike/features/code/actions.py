from dataclasses import dataclass
from analyst_klondike.state.base_action import BaseAction


@dataclass
class UpdateCodeAction(BaseAction):
    type = "UPDATE_CODE"
    code: str


@dataclass
class RunCodeAndSetResultsAction(BaseAction):
    type = "RUN_CODE_AND_SET_RESULTS"


@dataclass
class RunAllCodeAction(BaseAction):
    type = "RUN_ALL_CODE_ACTION"

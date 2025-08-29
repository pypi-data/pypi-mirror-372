from dataclasses import dataclass
from analyst_klondike.features.data_context.data_state import PythonTaskState
from analyst_klondike.state.base_action import BaseAction


@dataclass
class ImportTasksAction(BaseAction):
    type = "IMPORT_TASKS_ACTION"
    quiz_id: str
    tasks: list[PythonTaskState]


@dataclass
class SwitchToTeacherModeAction(BaseAction):
    type = "SWITCH_TO_TEACHER_MODE"

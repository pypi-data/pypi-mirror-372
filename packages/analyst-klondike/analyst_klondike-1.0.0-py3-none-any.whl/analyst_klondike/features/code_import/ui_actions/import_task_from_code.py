import os

from analyst_klondike.features.code_import.analysis.code_analysis import (
    create_quiz_from_code
)
from analyst_klondike.features.code_import.ui_actions.actions import ImportTasksAction
from analyst_klondike.state.app_dispatch import app_dispatch


def import_task_action(quiz_id: str, file_path: str | None) -> None:

    if file_path is None or not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not exists")

    with open(file_path, 'r', encoding='UTF-8') as f:
        code = f.read()
        python_tasks = create_quiz_from_code(quiz_id, code)
        app_dispatch(ImportTasksAction(quiz_id, python_tasks))

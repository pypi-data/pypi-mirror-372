from dataclasses import dataclass
from typing import Any
import yaml

from textual.app import App

from analyst_klondike.features.data_context.data_state import TestCaseState
from analyst_klondike.features.message_box.actions import DisplayMessageBoxAction
from analyst_klondike.state.app_dispatch import app_dispatch
from analyst_klondike.state.app_state import AppState
from analyst_klondike.state.base_action import BaseAction


@dataclass
class SaveAction(BaseAction):
    type = "SAVE_ACTION"


def save_to_yaml(state: AppState, app: App[Any]) -> None:
    try:
        _try_save(state)
        app.notify(
            "Сохранено",
            title=state.current.opened_file_name,
            severity="information",
            timeout=1
        )
    except Exception:  # pylint: disable=W0718
        app_dispatch(DisplayMessageBoxAction(
            f"Ошибка при сохранении файла {state.current.opened_file_name}"
        ))
        app.notify(
            "Не удалось сохранить",
            title=state.current.opened_file_name,
            severity="error",
            timeout=1
        )


def _try_save(state: AppState) -> None:
    with open(state.current.opened_file_path,
              encoding='utf-8',
              mode='w') as f:
        data = _create_json(state)
        yaml.dump(data, f,
                  allow_unicode=True,
                  encoding='UTF-8',
                  default_flow_style=False,
                  indent=2,
                  sort_keys=False)


def _create_json(state: AppState) -> Any:
    def _get_tasks(quiz_id: str):
        task_dict = {
            t.title: t for t in state.data.tasks.values() if t.quiz_id == quiz_id
        }
        return task_dict.items()

    d = {  # type: ignore
        "quiz_info": {
            "min_supported_app_version": state.current.opened_file_min_supported_app_version
        },
        "user_info": {
            "email": state.user_email
        },
        "quizes": {
            quiz_id: {
                "title": quiz.title,
                "questions": {
                    t_id: {
                        "text": t.description,
                        "code_template": t.code_template,
                        "code": t.code,
                        "test_cases": _test_cases_to_json(t.test_cases),
                        "is_passed": t.is_passed,
                        "params": _get_task_params(t.test_cases)
                    } for t_id, t in _get_tasks(quiz.id)
                }
            } for quiz_id, quiz in state.data.quizes.items()
        }
    }
    return d  # type: ignore


def _get_task_params(cases: list[TestCaseState]) -> dict[str, str]:
    param_dict: dict[str, str] = {}

    for c in cases:
        for inp in c.inputs:
            param_dict[inp.param_name] = inp.param_type
        param_dict["return"] = c.expected.param_type
    return param_dict


def _test_cases_to_json(cases: list[TestCaseState]) -> list[dict[str, str]]:
    test_cases: list[dict[str, str]] = []
    for c in cases:
        test_cases_dict: dict[str, str] = {}
        for inp in c.inputs:
            test_cases_dict[inp.param_name] = inp.param_value
        test_cases_dict["expected"] = c.expected.param_value
        test_cases.append(test_cases_dict)
    return test_cases

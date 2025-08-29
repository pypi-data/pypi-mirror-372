from dataclasses import dataclass
import analyst_klondike
from analyst_klondike.features.data_context.data_state import (
    PythonQuizState,
    PythonTaskResult,
    PythonTaskState,
    TestCaseState,
    VariableState
)
from analyst_klondike.features.data_context.json_load.dc import (
    JsonLoadResult,
    PythonQuizJson,
    QuestionJson,
    TestCaseJson)
from analyst_klondike.state.app_state import AppState
from analyst_klondike.state.base_action import BaseAction


@dataclass
class InitAction(BaseAction):
    type = "INIT_APP"
    data: JsonLoadResult


@dataclass
class ReadFileAndAppVersion(BaseAction):
    type = "INIT_FILE_AND_APP_VERSION"
    data: JsonLoadResult


def init_state(state: AppState, data: JsonLoadResult) -> None:
    state.user_email = "Клондайк аналитика"
    state.data.quizes = {
        x.id: _get_quiz_state(x) for x in data.quizes
    }
    state.data.tasks = {
        question.id: _get_question_state(question, quiz.id)
        for quiz in data.quizes
        for question in quiz.questions
    }
    state.current.app_title = _get_title(state)
    state.current.app_subtitle = _get_subtitle()
    state.current.app_version = analyst_klondike.__version__
    state.current.opened_file_min_supported_app_version = \
        data.quiz_info.min_supported_app_version


def _get_title(state: AppState) -> str:
    title = "Клондайк аналитика"
    if state.is_teacher_mode:
        title += " (teacher mode)"
    if state.event_sender == "no_events":
        title += " no events"
    return title


def _get_subtitle() -> str:
    return "Интерактивный тренажер Python на вашем " +\
        f"компьютере (version. {analyst_klondike.__version__})"


def init_file_and_app_version(state: AppState, data: JsonLoadResult) -> None:
    state.current.app_version = analyst_klondike.__version__
    state.current.opened_file_min_supported_app_version = \
        data.quiz_info.min_supported_app_version


def _get_quiz_state(data: PythonQuizJson) -> PythonQuizState:
    return PythonQuizState(
        id=data.id,
        title=data.title,
        is_node_expanded=False
    )


def _get_question_state(data: QuestionJson, quiz_id: str) -> PythonTaskState:
    def get_passed_status() -> PythonTaskResult:
        if data.is_passed == "passed":
            return "passed"
        if data.is_passed == "failed":
            return "failed"
        return "not_runned"

    return PythonTaskState(
        id=data.id,
        quiz_id=quiz_id,
        title=data.title,
        description=data.text,
        code_template=data.code_template,
        code=data.code if data.code != "" else data.code_template,
        test_cases=_get_test_cases(data.test_cases),
        is_passed=get_passed_status(),
    )


def _get_test_cases(cases: list[TestCaseJson]) -> list[TestCaseState]:
    return [
        TestCaseState(
            inputs=[VariableState(
                param_name=inp.param_name,
                param_type=inp.param_type,
                param_value=inp.param_value
            ) for inp in c.inputs],
            expected=VariableState(
                param_name=c.expected.param_name,
                param_value=c.expected.param_value,
                param_type=c.expected.param_type
            )
        )
        for c in cases
    ]

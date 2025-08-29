from datetime import datetime
from analyst_klondike.features.code.actions import (
    RunAllCodeAction,
    RunCodeAndSetResultsAction,
    UpdateCodeAction
)
from analyst_klondike.features.code.code_runner.runner import CodeRunner
from analyst_klondike.features.code.state import ResultCaseState
from analyst_klondike.features.data_context.data_state import PythonTaskState
from analyst_klondike.state.app_state import AppState
from analyst_klondike.state.base_action import BaseAction
from analyst_klondike.features.current.selectors import select_current_task


def apply(state: AppState, action: BaseAction) -> AppState:
    if isinstance(action, UpdateCodeAction):
        # update current code
        state.run_code.last_code = action.code

        # update current task code
        current_task = select_current_task(state)
        if current_task is not None:
            current_task.code = action.code

        # set code to run
        state.run_code.last_code = action.code
        return state
    if isinstance(action, RunCodeAndSetResultsAction):
        _run_and_set_results(state)
        return state
    if isinstance(action, RunAllCodeAction):
        _run_previously_runned_tasks(state)
    return state


def _run_and_set_results(state: AppState) -> None:
    current_task = select_current_task(state)
    if current_task is None:
        return
    _run_task(current_task, state)


def _run_previously_runned_tasks(state: AppState) -> None:
    runned_tasks = (t for t in state.data.tasks.values()
                    if t.is_passed in ("passed", "failed"))
    for task in runned_tasks:
        _run_task(task, state)


def _run_task(current_task: PythonTaskState, state: AppState) -> None:
    # run code here and set results
    res = CodeRunner(function_name="solution").run_code(
        current_task.test_cases,
        current_task.code)

    # set last code run info
    state.run_code.last_run_dt = datetime.now()
    state.run_code.last_code = current_task.code

    state.run_code.result_cases = [
        ResultCaseState(
            func_params=r.func_params,
            expected=r.expected,
            actual=r.actual,
            passed=r.passed,
            has_exception=r.exception is not None,
            exception_message=r.exception,
            printed_lines=r.printed_lines
        ) for r in res.all_cases
    ]
    # add test case errors
    state.run_code.errors = list(res.errors)
    state.run_code.has_errors = len(res.errors) > 0

    are_all_tests_passed = all(c.passed for c in res.all_cases)

    is_task_passed = not state.run_code.has_errors and are_all_tests_passed

    # set run result:
    current_task.is_passed = "passed" if is_task_passed else "failed"

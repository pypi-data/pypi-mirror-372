from analyst_klondike.features.code.state import ResultCaseState
from analyst_klondike.state.app_state import AppState


def has_failed_cases(state: AppState) -> bool:
    return any(not r.passed for r in state.run_code.result_cases)


def select_first_failed_case(state: AppState) -> ResultCaseState:
    failed_cases = (c for c in state.run_code.result_cases if not c.passed)
    return next(failed_cases)


def are_all_cases_passed(state: AppState) -> bool:
    return all(c.passed for c in state.run_code.result_cases)


def has_cases(state: AppState) -> bool:
    return len(state.run_code.result_cases) > 0

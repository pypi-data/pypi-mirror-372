from datetime import datetime
from textual.app import ComposeResult
from textual.widgets import ListView, ListItem
from textual.containers import Vertical
from rich.text import Text


from analyst_klondike.features.code.actions import RunCodeAndSetResultsAction
from analyst_klondike.features.code.state import ResultCaseState
from analyst_klondike.state.app_state import AppState, select
from analyst_klondike.features.code.selector import (
    has_cases,
    are_all_cases_passed,
    has_failed_cases,
    select_first_failed_case
)


class TestResultItem(ListItem):

    DEFAULT_CSS = """
        TestResultItem {
            height: 1;
        }
    """

    def __init__(self, res: ResultCaseState):
        super().__init__()
        self._res = res

    def render(self) -> Text:
        if self._res.passed:
            return Text.from_markup(":green_circle: Test passed")
        return self._failed_markup()

    def _failed_markup(self) -> Text:
        if self._res.has_exception:
            return Text.from_markup(f":red_circle: {self._res.exception_message}")
        expected = self._res.expected
        actual = self._res.actual
        params_str = ",".join(f"{k} = {v}" for k, v
                              in self._res.func_params.items())
        comparison_result = Text.from_markup(f":red_circle: Failed for {params_str}. " +
                                             f"Expected = {expected}, " +
                                             f"but having = {actual}")
        return comparison_result + "\n" + self._get_printed_lines()

    def _get_printed_lines(self) -> Text:
        printed_lines = self._res.printed_lines
        return Text.from_markup("\n".join(str(line) for line in printed_lines))


class ErrorResultItem(ListItem):
    def __init__(self, error: str) -> None:
        super().__init__()
        self._error = error

    def render(self) -> Text:
        return Text.from_markup(f":red_circle: {self._error}")


class AllTestsPassedResultItem(ListItem):

    def render(self) -> Text:
        return Text.from_markup(":green_circle: задача решена!")


class TestResults(Vertical):

    DEFAULT_CSS = """
        TestResults {
            border: solid $primary;
            
            ListView {
                background: $background;

                ListItem {
                    background: $background;
                }
            }
        }

        """

    def __init__(self) -> None:
        super().__init__()

    def on_mount(self) -> None:
        self.border_title = "Результаты"

    def compose(self) -> ComposeResult:
        yield ListView()

    def update_view(self, state: AppState) -> None:
        if state.last_action_type != RunCodeAndSetResultsAction.type:
            return
        list_view = self.query_one("ListView", ListView)
        list_view.clear()
        # if has errors then append errors in list
        if state.run_code.has_errors:
            for err in state.run_code.errors:
                list_view.append(ErrorResultItem(err))
            return

        any_cases = select(has_cases)
        all_passed = select(are_all_cases_passed)
        any_failed = select(has_failed_cases)

        if all_passed and any_cases:
            list_view.append(AllTestsPassedResultItem())
            return
        if any_failed:
            first_failed = select(select_first_failed_case)
            list_view.append(TestResultItem(first_failed))

        if state.run_code.last_code != "":
            self.border_title = f"Результаты: {datetime.strftime(state.run_code.last_run_dt,
                                                                 "%H:%M:%S")}"

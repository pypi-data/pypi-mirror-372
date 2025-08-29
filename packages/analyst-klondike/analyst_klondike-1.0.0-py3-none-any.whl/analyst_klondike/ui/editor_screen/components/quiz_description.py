from textual.app import ComposeResult
from textual.reactive import var
from textual.containers import Vertical
from textual.widgets import Static

from analyst_klondike.state.app_state import INITIAL_STATE, AppState
from analyst_klondike.features.current.selectors import select_current_quiz


class QuizDescription(Vertical):

    state = var(INITIAL_STATE, init=False)

    DEFAULT_CSS = """
        QuizDescription {
            border: solid $primary;
            padding: 1;
        }
    """

    def on_mount(self) -> None:
        self.border_title = "Тест"

    def compose(self) -> ComposeResult:
        yield Static("Hello, quiz")

    def watch_state(self, new_state: AppState):
        static = self.query_one("Static", Static)
        current_quiz = select_current_quiz(new_state)
        if current_quiz is not None:
            self.border_title = current_quiz.title
            static.update(current_quiz.title)

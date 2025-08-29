from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Vertical
from textual.reactive import var

from analyst_klondike.state.app_state import INITIAL_STATE, AppState


class CurrentTaskInfo(Vertical):

    DEFAULT_CSS = """
        CurrentTaskInfo {
            border: solid $primary;
            background: $background;
            height: 1fr;
            padding: 1;
        }
    """

    state = var(INITIAL_STATE, init=False)

    def on_mount(self) -> None:
        self.border_title = "Задача"

    def compose(self) -> ComposeResult:
        yield Static(id="task_text", markup=False)

    def watch_state(self, new_state: AppState) -> None:
        selected_task_id = new_state.current.task_id
        if selected_task_id is not None:
            task = new_state.data.tasks[selected_task_id]
            static = self.query_one("Static", Static)
            static.update(task.description)

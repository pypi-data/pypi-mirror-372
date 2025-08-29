from textual import on
from textual.message import Message
from textual.app import ComposeResult
from textual.widgets import TextArea
from textual.containers import VerticalScroll
from textual.reactive import var

from analyst_klondike.features.current.actions import MakeTaskCurrentAction
from analyst_klondike.features.app.actions import ChangeThemeAction
from analyst_klondike.state.app_state import INITIAL_STATE, AppState
from analyst_klondike.features.current.selectors import select_current_task


class CodeEditor(VerticalScroll):

    DEFAULT_CSS = """
        CodeEditor {
            border: solid $primary;

            TextArea {
                border: none;
                
                &:focus-within {
                    border: none;
                }
            }
        }
    """

    class CodeUpdated(Message):
        def __init__(self, code: str) -> None:
            super().__init__()
            self.code = code

    state: var[AppState] = var(INITIAL_STATE, init=False)

    def on_mount(self):
        self.border_title = "Редактор"
        textarea = self.query_one("TextArea", TextArea)
        textarea.indent_type = "tabs"

    def compose(self) -> ComposeResult:
        code_editor = TextArea.code_editor("",
                                           theme="monokai",
                                           language="python",
                                           id="code_editor")
        yield code_editor

    def watch_state(self, state: AppState) -> None:
        if state.last_action_type in (MakeTaskCurrentAction.type):
            task = select_current_task(state)
            editor = self.query_one("TextArea", TextArea)
            if task is None:
                return
            with editor.prevent(TextArea.Changed):
                editor.text = task.code
        if state.last_action_type == ChangeThemeAction.type:
            editor = self.query_one("TextArea", TextArea)
            if state.is_dark:
                editor.theme = 'monokai'
            else:
                editor.theme = 'github_light'

    @on(TextArea.Changed)
    def on_textarea_changed(self, event: TextArea.Changed) -> None:
        new_code = event.text_area.text
        self.post_message(CodeEditor.CodeUpdated(new_code))

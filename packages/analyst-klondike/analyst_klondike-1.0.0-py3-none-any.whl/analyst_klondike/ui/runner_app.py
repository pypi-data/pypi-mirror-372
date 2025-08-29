from typing import Any, Callable
from textual import on
from textual.app import App
import pyperclip


from analyst_klondike.features.current.selectors import select_has_file_openned
from analyst_klondike.features.data_context.save_action import save_to_yaml
from analyst_klondike.features.app.actions import ChangeThemeAction
from analyst_klondike.features.demo_quiz.demo import start_demo_quiz
from analyst_klondike.features.events.event_hook import send_event
from analyst_klondike.state.app_dispatch import app_dispatch
from analyst_klondike.state.app_state import AppState, get_state, select
from analyst_klondike.ui.editor_screen.editor import EditorScreen
from analyst_klondike.ui.file_screen.save_file_before_exit_screen import (
    SaveOnExitModal,
    SaveOrExitModalResult
)


class RunnerApp(App[Any]):
    COMMAND_PALETTE_BINDING = "ctrl+backslash"
    EDITOR_SCREEN = EditorScreen()

    def __init__(self) -> None:
        super().__init__()
        self.on_mounted_callback: Callable[[], None] | None = None

    def update_view(self, state: AppState) -> None:
        RunnerApp.EDITOR_SCREEN.update_view(state)

    def on_mount(self) -> None:
        self.push_screen(RunnerApp.EDITOR_SCREEN)
        self.theme = "gruvbox"
        self.title = "Клондайк аналитика"
        self.sub_title = "Интерактивный тренажер Python на вашем компьютере"
        if self.on_mounted_callback is not None:
            self.on_mounted_callback()

    @on(EditorScreen.UpdateAppTitleMessage)
    def on_title_subtitle_changed(self, event: EditorScreen.UpdateAppTitleMessage) -> None:
        self.title = event.title
        self.sub_title = event.subtitle

    async def action_quit(self):

        def on_screen_get_result(res: SaveOrExitModalResult | None) -> None:
            if res == "cancel":
                return
            if res == "save":
                state = get_state()
                save_to_yaml(state, self.app)
            send_event("app_normally_closed", "/")
            self.app.exit(0)
        has_file = select(select_has_file_openned)
        if has_file:
            self.push_screen(SaveOnExitModal(), on_screen_get_result)
        else:
            send_event("app_normally_closed", "/", async_run=False)
            self.exit(0)

    def watch_theme(self, new_theme: Any) -> None:
        app_dispatch(ChangeThemeAction(
            theme=new_theme,
            is_dark=self.current_theme.dark
        ))

    # This action is used in wellcome message
    def action_start_demo_test(self) -> None:
        start_demo_quiz()

    # Copy to clipboard update string
    def action_copy_update_str_to_clipboard(self) -> None:
        try:
            pyperclip.copy('uv tool upgrade analyst-klondike')
            self.notify(
                message="Скопировано uv tool upgrade analyst-klondike",
                title="Клондайк аналитика",
                severity="information"
            )
            send_event("update_command_is_copied", "/")
        except Exception:  # pylint: disable=W0718
            self.notify(
                message="Ошибка при копировании uv tool upgrade analyst-klondike в буфер обмена",
                title="Клондайк аналитика",
                severity="error"
            )


_app = RunnerApp()


def get_app() -> RunnerApp:
    return _app

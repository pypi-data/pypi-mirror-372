import os
from textual import on
from textual.reactive import var
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Grid, Horizontal
from textual.widgets import Button, Label, DirectoryTree


class OpenFileScreen(ModalScreen[str]):

    CSS_PATH = "open_file_screen.tcss"
    selected_path = var("")

    def on_mount(self) -> None:
        open_button = self.query_one("#open", Button)
        open_button.disabled = True

    def compose(self) -> ComposeResult:
        with Grid(id="dialog"):
            yield Label("Выберите файл", id="modal_question")
            yield DirectoryTree("./")
            with Horizontal():
                yield Button("Открыть", id="open", variant="primary")
                yield Button("Отмена", id="cancel", variant="error")

    @on(DirectoryTree.FileSelected)
    def on_file_selected(self, ev: DirectoryTree.FileSelected) -> None:
        self.selected_path = str(ev.path)
        open_button = self.query_one("#open", Button)
        open_button.disabled = not os.path.exists(self.selected_path)

    @on(Button.Pressed, "#open")
    def on_ok_button_pressed(self) -> None:
        self.dismiss(self.selected_path)

    @on(Button.Pressed, "#cancel")
    def on_cancel_button_pressed(self) -> None:
        self.dismiss(None)

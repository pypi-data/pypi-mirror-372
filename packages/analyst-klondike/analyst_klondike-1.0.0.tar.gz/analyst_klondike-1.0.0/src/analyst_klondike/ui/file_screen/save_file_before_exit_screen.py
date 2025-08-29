from typing import Literal
from textual import on
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal, Container
from textual.widgets import Label, Button

SaveOrExitModalResult = Literal["save", "not_save", "cancel"]


class SaveOnExitModal(ModalScreen[SaveOrExitModalResult]):

    CSS_PATH = "save_on_exit_modal.tcss"

    def compose(self) -> ComposeResult:
        yield Container(id="shadow")
        with Vertical(id="dialog"):
            yield Label("Сохранить файл?")
            with Horizontal(id="buttons"):
                yield Button(id="save", label="Сохранить", variant="success")
                yield Button(id="not_save", label="Не сохранять", variant="error")
                yield Button(id="cancel", label="Отмена", variant="default")

    @on(Button.Pressed, "#save")
    def on_save_button_clicked(self) -> None:
        self.dismiss("save")

    @on(Button.Pressed, "#not_save")
    def on_not_save_button_clicked(self) -> None:
        self.dismiss("not_save")

    @on(Button.Pressed, "#cancel")
    def on_cancel_button_clicked(self) -> None:
        self.dismiss("cancel")

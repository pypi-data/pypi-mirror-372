from textwrap import dedent
from rich.text import Text
from textual import on
from textual.reactive import reactive
from textual.app import ComposeResult
from textual.containers import (
    Vertical,
    Horizontal,
    Container,
    VerticalScroll)
from textual.widget import Widget
from textual.widgets import Button, Static
from textual.screen import ModalScreen
from analyst_klondike.state.app_state import AppState, get_state, select


class MessageText(Widget):

    markup_text = reactive("")

    def __init__(self, text: str) -> None:
        super().__init__()
        self.markup_text = text

    def render(self) -> Text:
        return Text.from_markup(self.markup_text)


class MessageBoxScreen(ModalScreen[bool]):

    @staticmethod
    def message(state: AppState) -> str:
        return dedent(state.message_box.message)

    CSS_PATH = "mb_screen.tcss"

    def compose(self) -> ComposeResult:
        msg_text = select(MessageBoxScreen.message)
        yield Container(id="shadow")
        with Vertical(id="dialog"):
            with VerticalScroll():
                yield Static(msg_text)
            with Horizontal(id="buttons"):
                yield Button(id="ok_button",
                             label="ОК",
                             variant="success")

    @on(Button.Pressed, "#ok_button")
    def ok_button_click(self) -> None:
        state = get_state()
        if state.message_box.ok_button_callback is not None:
            state.message_box.ok_button_callback()
        self.dismiss(True)
